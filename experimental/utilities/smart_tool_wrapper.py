"""
Smart Tool Wrapper - Prevents Redundant Tool Calls

Wraps LangChain tools with intelligence to prevent:
- Duplicate tool calls with identical parameters
- Infinite retry loops
- Excessive API calls

Usage:
    from experimental.utilities.smart_tool_wrapper import wrap_tools_with_dedup

    # Wrap your tools
    smart_tools = wrap_tools_with_dedup(tools, max_retries=3)

    # Use in agent
    agent = create_react_agent(model=llm, tools=smart_tools, ...)
"""

import json
import hashlib
import logging
import time
from typing import Any, Dict, List, Callable
from langchain_core.tools import StructuredTool
from functools import wraps

logger = logging.getLogger(__name__)


class ToolCallTracker:
    """Tracks tool calls to prevent redundant queries"""

    def __init__(self, max_retries: int = 3, cache_ttl: int = 300):
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl  # Time-to-live in seconds (default: 5 minutes)
        self.call_history = []  # List of (tool_name, args_hash)
        self.cache = {}  # args_hash -> result
        self.cache_timestamps = {}  # args_hash -> timestamp
        self.consecutive_failures = 0

    def get_call_signature(self, tool_name: str, **kwargs) -> str:
        """Generate unique signature for a tool call"""
        # Sort kwargs to ensure consistent hashing
        sorted_kwargs = json.dumps(kwargs, sort_keys=True, default=str)
        signature = f"{tool_name}:{sorted_kwargs}"
        return hashlib.md5(signature.encode()).hexdigest()

    def should_allow_call(self, tool_name: str, signature: str) -> tuple[bool, str]:
        """Check if this call should be allowed"""
        # Count how many times this exact call has been made
        call_count = self.call_history.count((tool_name, signature))

        if call_count >= self.max_retries:
            return False, f"DUPLICATE_CALL_LIMIT: This exact query has been attempted {call_count} times. Please try a different approach or parameters."

        # Check for rapid consecutive identical calls (loop detection)
        if len(self.call_history) >= 3:
            last_3 = self.call_history[-3:]
            if all(call == (tool_name, signature) for call in last_3):
                return False, f"LOOP_DETECTED: Making the same call repeatedly. Try a different strategy."

        return True, ""

    def record_call(self, tool_name: str, signature: str, result: Any, success: bool):
        """Record a tool call"""
        self.call_history.append((tool_name, signature))

        # Track consecutive failures
        if not success:
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0
            # Cache successful results with timestamp
            self.cache[signature] = result
            self.cache_timestamps[signature] = time.time()

    def get_cached_result(self, signature: str) -> tuple[bool, Any]:
        """Check if we have a cached result (with TTL check)"""
        if signature in self.cache:
            # Check if cache entry has expired
            cache_age = time.time() - self.cache_timestamps.get(signature, 0)
            if cache_age < self.cache_ttl:
                return True, self.cache[signature]
            else:
                # Cache expired - remove it
                logger.info(f"[CACHE EXPIRED] Removing stale cache entry (age: {cache_age:.1f}s)")
                del self.cache[signature]
                del self.cache_timestamps[signature]
        return False, None

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tool usage"""
        return {
            "total_calls": len(self.call_history),
            "unique_calls": len(set(self.call_history)),
            "cached_results": len(self.cache),
            "consecutive_failures": self.consecutive_failures
        }


# Global tracker (persists across agent iterations) with 5-minute TTL
_global_tracker = ToolCallTracker(max_retries=3, cache_ttl=300)


def create_smart_wrapper(tool: StructuredTool, tracker: ToolCallTracker) -> StructuredTool:
    """Create a smart wrapper around a tool"""

    original_func = tool.func

    @wraps(original_func)
    def smart_func(**kwargs):
        tool_name = tool.name

        # Generate call signature
        signature = tracker.get_call_signature(tool_name, **kwargs)

        # Check cache first
        has_cache, cached_result = tracker.get_cached_result(signature)
        if has_cache:
            logger.info(f"[CACHE HIT] {tool_name} - returning cached result")
            return f"[CACHED RESULT] {cached_result}"

        # Check if we should allow this call
        allowed, reason = tracker.should_allow_call(tool_name, signature)
        if not allowed:
            logger.warning(f"[BLOCKED] {tool_name} - {reason}")
            return f"ERROR: {reason}\n\nSuggestion: Try modifying your query parameters or using a different approach."

        # Execute the actual tool
        try:
            logger.info(f"[EXECUTING] {tool_name} (attempt {tracker.call_history.count((tool_name, signature)) + 1})")
            result = original_func(**kwargs)

            # Detect if result indicates an error
            success = "error" not in str(result).lower() and "failed" not in str(result).lower()

            # Record the call
            tracker.record_call(tool_name, signature, result, success)

            return result

        except Exception as e:
            logger.error(f"[ERROR] {tool_name} - {str(e)}")
            tracker.record_call(tool_name, signature, str(e), success=False)
            return f"ERROR: {str(e)}\n\nThis query failed. Consider trying a different approach."

    # Create new StructuredTool with smart wrapper
    return StructuredTool(
        name=tool.name,
        description=tool.description,
        func=smart_func,
        args_schema=tool.args_schema
    )


def wrap_tools_with_dedup(
    tools: List[StructuredTool],
    max_retries: int = 3,
    use_global_tracker: bool = True,
    cache_ttl: int = 300
) -> List[StructuredTool]:
    """
    Wrap tools with deduplication and smart retry logic.

    Args:
        tools: List of LangChain StructuredTool instances
        max_retries: Maximum number of times to allow identical call (default: 3)
        use_global_tracker: Use global tracker across agent sessions (default: True)
        cache_ttl: Time-to-live for cached results in seconds (default: 300 = 5 minutes)

    Returns:
        List of wrapped tools with smart deduplication
    """
    tracker = _global_tracker if use_global_tracker else ToolCallTracker(max_retries, cache_ttl)

    smart_tools = []
    for tool in tools:
        smart_tool = create_smart_wrapper(tool, tracker)
        smart_tools.append(smart_tool)

    logger.info(f"Wrapped {len(tools)} tools with smart deduplication (max_retries={max_retries})")

    return smart_tools


def reset_tracker():
    """Reset the global tracker (useful for testing)"""
    global _global_tracker
    _global_tracker = ToolCallTracker(max_retries=3, cache_ttl=300)
    logger.info("Reset global tool call tracker")


def get_tracker_stats() -> Dict[str, Any]:
    """Get statistics from the global tracker"""
    return _global_tracker.get_stats()
