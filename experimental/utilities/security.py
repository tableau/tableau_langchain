"""
Security and Rate Limiting Module for OpenAI API Protection
Provides guardrails against unauthorized access and excessive API usage.
"""
import os
import time
import hashlib
import logging
import re
from typing import Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Try to import language detection library
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_usage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Implements token bucket rate limiting per IP address and API key.
    """
    def __init__(self):
        # Stores: {identifier: {'tokens': float, 'last_update': float}}
        self.buckets: Dict[str, Dict] = defaultdict(lambda: {
            'tokens': 0,
            'last_update': time.time()
        })

        # Rate limiting configuration from environment or defaults
        self.max_requests_per_minute = int(os.getenv('RATE_LIMIT_PER_MINUTE', '10'))
        self.max_requests_per_hour = int(os.getenv('RATE_LIMIT_PER_HOUR', '100'))
        self.max_requests_per_day = int(os.getenv('RATE_LIMIT_PER_DAY', '1000'))

    def _get_identifier(self, request) -> str:
        """Generate unique identifier for rate limiting."""
        api_key = request.headers.get('X-API-Key', '')
        ip_address = request.remote_addr or 'unknown'

        if api_key:
            # Hash API key for privacy
            return hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return ip_address

    def _refill_tokens(self, bucket: Dict, max_tokens: int, refill_rate: float) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket['last_update']
        bucket['tokens'] = min(max_tokens, bucket['tokens'] + elapsed * refill_rate)
        bucket['last_update'] = now

    def is_allowed(self, request, tokens_required: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Check if request is allowed based on rate limits.
        Returns (is_allowed, error_message)
        """
        identifier = self._get_identifier(request)
        bucket = self.buckets[identifier]

        # Refill tokens (1 token per 6 seconds = 10 per minute)
        refill_rate = self.max_requests_per_minute / 60.0
        self._refill_tokens(bucket, self.max_requests_per_minute, refill_rate)

        if bucket['tokens'] >= tokens_required:
            bucket['tokens'] -= tokens_required
            logger.info(f"Request allowed for {identifier}. Tokens remaining: {bucket['tokens']:.2f}")
            return True, None
        else:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False, f"Rate limit exceeded. Max {self.max_requests_per_minute} requests per minute."


class UsageTracker:
    """
    Tracks API usage and costs to prevent budget overruns.
    """
    def __init__(self):
        self.usage_log: Dict[str, list] = defaultdict(list)

        # Cost tracking (approximate token costs for GPT-4o-mini and embeddings)
        self.cost_per_1k_tokens = {
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'gpt-4o': {'input': 0.0025, 'output': 0.01},
            'text-embedding-3-small': {'input': 0.00002, 'output': 0}
        }

        # Budget limits from environment
        self.daily_budget = float(os.getenv('DAILY_BUDGET_USD', '10.0'))
        self.hourly_budget = float(os.getenv('HOURLY_BUDGET_USD', '2.0'))

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int = 0) -> float:
        """Estimate cost for a request."""
        costs = self.cost_per_1k_tokens.get(model, self.cost_per_1k_tokens['gpt-4o-mini'])
        input_cost = (input_tokens / 1000) * costs['input']
        output_cost = (output_tokens / 1000) * costs['output']
        return input_cost + output_cost

    def track_usage(self, identifier: str, model: str, input_tokens: int, output_tokens: int = 0):
        """Track usage for an identifier."""
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        self.usage_log[identifier].append({
            'timestamp': datetime.now(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost
        })

        logger.info(f"Usage tracked - ID: {identifier}, Model: {model}, "
                   f"Tokens: {input_tokens}+{output_tokens}, Cost: ${cost:.4f}")

        # Clean old entries (older than 24 hours)
        self._cleanup_old_entries(identifier)

    def _cleanup_old_entries(self, identifier: str):
        """Remove entries older than 24 hours."""
        cutoff = datetime.now() - timedelta(hours=24)
        self.usage_log[identifier] = [
            entry for entry in self.usage_log[identifier]
            if entry['timestamp'] > cutoff
        ]

    def check_budget(self, identifier: str) -> Tuple[bool, Optional[str]]:
        """Check if identifier is within budget limits."""
        now = datetime.now()
        hourly_cutoff = now - timedelta(hours=1)
        daily_cutoff = now - timedelta(hours=24)

        entries = self.usage_log[identifier]

        # Calculate hourly and daily costs
        hourly_cost = sum(e['cost'] for e in entries if e['timestamp'] > hourly_cutoff)
        daily_cost = sum(e['cost'] for e in entries if e['timestamp'] > daily_cutoff)

        if hourly_cost >= self.hourly_budget:
            logger.error(f"Hourly budget exceeded for {identifier}: ${hourly_cost:.4f}")
            return False, f"Hourly budget exceeded. Limit: ${self.hourly_budget}"

        if daily_cost >= self.daily_budget:
            logger.error(f"Daily budget exceeded for {identifier}: ${daily_cost:.4f}")
            return False, f"Daily budget exceeded. Limit: ${self.daily_budget}"

        return True, None


class APIKeyValidator:
    """
    Validates API keys against a whitelist.
    """
    def __init__(self):
        # Load allowed API keys from environment (comma-separated)
        self.allowed_keys = set(
            key.strip() for key in os.getenv('ALLOWED_API_KEYS', '').split(',')
            if key.strip()
        )

        # If no keys specified, allow all (development mode)
        self.enforce_auth = len(self.allowed_keys) > 0

        if not self.enforce_auth:
            logger.warning("⚠️  API authentication is DISABLED. Set ALLOWED_API_KEYS in production!")

    def validate(self, api_key: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Validate API key."""
        if not self.enforce_auth:
            return True, None

        if not api_key:
            return False, "API key required. Provide 'X-API-Key' header."

        if api_key not in self.allowed_keys:
            logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
            return False, "Invalid API key."

        return True, None


# Global instances
rate_limiter = RateLimiter()
usage_tracker = UsageTracker()
api_key_validator = APIKeyValidator()


def require_api_key(f):
    """Decorator to enforce API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        is_valid, error = api_key_validator.validate(api_key)
        if not is_valid:
            logger.warning(f"Authentication failed from {request.remote_addr}")
            return jsonify({"error": error, "status": "unauthorized"}), 401

        return f(*args, **kwargs)
    return decorated_function


def rate_limit(tokens_required: int = 1):
    """Decorator to enforce rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_allowed, error = rate_limiter.is_allowed(request, tokens_required)
            if not is_allowed:
                return jsonify({
                    "error": error,
                    "status": "rate_limit_exceeded",
                    "retry_after": "60 seconds"
                }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_budget():
    """Decorator to enforce budget limits."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = rate_limiter._get_identifier(request)
            is_within_budget, error = usage_tracker.check_budget(identifier)

            if not is_within_budget:
                return jsonify({
                    "error": error,
                    "status": "budget_exceeded",
                    "message": "Contact administrator to increase limits"
                }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_request():
    """Decorator to log all API requests."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

            start_time = time.time()
            response = f(*args, **kwargs)
            elapsed = time.time() - start_time

            logger.info(f"Response completed in {elapsed:.3f}s")
            return response
        return decorated_function
    return decorator


def detect_language(text: str) -> Optional[str]:
    """
    Detect the language of the input text.
    Returns language code (e.g., 'en', 'es', 'zh-cn') or None if detection fails.
    """
    if not text or len(text.strip()) < 3:
        return None

    # If langdetect is available, use it
    if LANGDETECT_AVAILABLE:
        try:
            return detect(text)
        except LangDetectException:
            pass

    # Fallback: Simple heuristic check for non-English characters
    # Count non-ASCII characters
    non_ascii_count = sum(1 for c in text if ord(c) > 127)
    total_chars = len(text)

    # If more than 30% non-ASCII, likely not English
    if total_chars > 0 and (non_ascii_count / total_chars) > 0.3:
        return 'unknown-non-english'

    # Check for common non-English unicode ranges
    # Cyrillic, Arabic, Chinese/Japanese/Korean, etc.
    cyrillic = re.search(r'[\u0400-\u04FF]', text)
    arabic = re.search(r'[\u0600-\u06FF]', text)
    cjk = re.search(r'[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]', text)

    if cyrillic or arabic or cjk:
        return 'non-english-unicode'

    return 'en'  # Assume English if no non-English patterns detected


def require_english():
    """
    Decorator to enforce English-only requests.
    Blocks requests with non-English content.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if language filtering is enabled
            if not os.getenv('BLOCK_NON_ENGLISH', 'false').lower() == 'true':
                return f(*args, **kwargs)

            # Get text from request (form data or JSON)
            text_to_check = None

            if request.is_json:
                data = request.get_json()
                # Check common fields
                for field in ['query', 'text', 'message', 'input', 'prompt']:
                    if field in data:
                        text_to_check = data[field]
                        break
            else:
                # Check form data
                for field in ['query', 'text', 'message', 'input', 'prompt']:
                    if field in request.form:
                        text_to_check = request.form.get(field)
                        break

            if text_to_check:
                detected_lang = detect_language(text_to_check)

                if detected_lang and detected_lang != 'en':
                    ip = request.remote_addr
                    logger.warning(
                        f"🚫 Blocked non-English request from {ip}. "
                        f"Detected language: {detected_lang}. "
                        f"Text: {text_to_check[:50]}..."
                    )

                    # Record violation for potential IP blocking
                    from experimental.utilities.ip_blocker import ip_blocker
                    ip_blocker.record_violation(ip, "non-english-content")

                    return jsonify({
                        "error": "Only English language requests are accepted",
                        "status": "language_not_supported",
                        "detected_language": detected_lang if detected_lang != 'unknown-non-english' and detected_lang != 'non-english-unicode' else 'non-english'
                    }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_environment():
    """
    Validate that required environment variables are set and secure.
    Call this on application startup.
    """
    required_vars = ['OPENAI_API_KEY']
    optional_vars = {
        'ALLOWED_API_KEYS': 'Authentication disabled - set this in production!',
        'RATE_LIMIT_PER_MINUTE': '10',
        'RATE_LIMIT_PER_HOUR': '100',
        'RATE_LIMIT_PER_DAY': '1000',
        'DAILY_BUDGET_USD': '10.0',
        'HOURLY_BUDGET_USD': '2.0'
    }

    errors = []
    warnings = []

    # Check required variables
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"❌ Missing required environment variable: {var}")

    # Check optional variables
    for var, default in optional_vars.items():
        if not os.getenv(var):
            warnings.append(f"⚠️  {var} not set. Using default: {default}")

    # Print summary
    if errors:
        logger.error("Environment validation failed:")
        for error in errors:
            logger.error(error)
        raise EnvironmentError("Missing required environment variables")

    if warnings:
        logger.warning("Environment validation warnings:")
        for warning in warnings:
            logger.warning(warning)

    logger.info("✅ Environment validation passed")

    # Log security status
    logger.info(f"Security Status:")
    logger.info(f"  - API Authentication: {'ENABLED' if api_key_validator.enforce_auth else 'DISABLED ⚠️'}")
    logger.info(f"  - Rate Limiting: {rate_limiter.max_requests_per_minute}/min, {rate_limiter.max_requests_per_hour}/hour")
    logger.info(f"  - Budget Limits: ${usage_tracker.hourly_budget}/hour, ${usage_tracker.daily_budget}/day")

