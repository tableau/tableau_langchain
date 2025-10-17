"""
IP Blocking and Allowlisting Module

Provides functionality to block malicious IPs and maintain an allowlist.
"""

import os
import json
import logging
from typing import Set, Optional
from datetime import datetime
from flask import request

logger = logging.getLogger(__name__)


class IPBlocker:
    """
    Manages IP blocking and allowlisting.
    """

    def __init__(self, blocklist_file: str = 'blocked_ips.json', allowlist_file: str = 'allowed_ips.json'):
        self.blocklist_file = blocklist_file
        self.allowlist_file = allowlist_file

        self.blocked_ips: Set[str] = self._load_set(blocklist_file)
        self.allowed_ips: Set[str] = self._load_set(allowlist_file)

        # Auto-block configuration
        self.auto_block_enabled = os.getenv('AUTO_BLOCK_ENABLED', 'false').lower() == 'true'
        self.auto_block_threshold = int(os.getenv('AUTO_BLOCK_THRESHOLD', '10'))  # violations before auto-block

        # Track violations per IP
        self.violations = {}  # {ip: count}

        logger.info(f"IP Blocker initialized. Blocked IPs: {len(self.blocked_ips)}, Allowed IPs: {len(self.allowed_ips)}")

    def _load_set(self, filename: str) -> Set[str]:
        """Load IP set from JSON file."""
        if not os.path.exists(filename):
            return set()

        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                return set(data.get('ips', []))
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return set()

    def _save_set(self, ips: Set[str], filename: str) -> None:
        """Save IP set to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'ips': list(ips),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")

    def is_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked."""
        # Allowlist takes precedence
        if ip in self.allowed_ips:
            return False

        return ip in self.blocked_ips

    def block_ip(self, ip: str, reason: str = "Manual block") -> None:
        """Add an IP to the blocklist."""
        if ip not in self.blocked_ips:
            self.blocked_ips.add(ip)
            self._save_set(self.blocked_ips, self.blocklist_file)
            logger.warning(f"🚫 Blocked IP: {ip} - Reason: {reason}")

    def unblock_ip(self, ip: str) -> None:
        """Remove an IP from the blocklist."""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            self._save_set(self.blocked_ips, self.blocklist_file)
            logger.info(f"✅ Unblocked IP: {ip}")

    def allow_ip(self, ip: str) -> None:
        """Add an IP to the allowlist (bypass all blocks)."""
        if ip not in self.allowed_ips:
            self.allowed_ips.add(ip)
            self._save_set(self.allowed_ips, self.allowlist_file)
            logger.info(f"✅ Added to allowlist: {ip}")

    def record_violation(self, ip: str, violation_type: str = "generic") -> None:
        """
        Record a violation for an IP. Auto-block if threshold exceeded.
        """
        # Don't track violations for allowed IPs
        if ip in self.allowed_ips:
            return

        if ip not in self.violations:
            self.violations[ip] = 0

        self.violations[ip] += 1
        logger.warning(f"⚠️  Violation recorded for {ip} ({violation_type}). Count: {self.violations[ip]}")

        # Auto-block if threshold exceeded
        if self.auto_block_enabled and self.violations[ip] >= self.auto_block_threshold:
            self.block_ip(ip, f"Auto-blocked after {self.violations[ip]} violations ({violation_type})")
            self.violations[ip] = 0  # Reset counter

    def get_blocked_ips(self) -> list:
        """Get list of all blocked IPs."""
        return list(self.blocked_ips)

    def get_allowed_ips(self) -> list:
        """Get list of all allowed IPs."""
        return list(self.allowed_ips)

    def get_stats(self) -> dict:
        """Get IP blocking statistics."""
        return {
            'blocked_count': len(self.blocked_ips),
            'allowed_count': len(self.allowed_ips),
            'violations_tracked': len(self.violations),
            'auto_block_enabled': self.auto_block_enabled,
            'auto_block_threshold': self.auto_block_threshold
        }


# Global instance
ip_blocker = IPBlocker()


def check_ip_blocked():
    """
    Decorator to check if request IP is blocked.
    Use this on routes you want to protect.
    """
    def decorator(f):
        from functools import wraps
        from flask import jsonify

        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr or 'unknown'

            if ip_blocker.is_blocked(ip):
                logger.warning(f"🚫 Blocked request from {ip}")
                return jsonify({
                    "error": "Access denied",
                    "message": "Your IP address has been blocked due to suspicious activity. Contact support if you believe this is an error."
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# CLI functions for manual IP management
def cli_block_ip():
    """CLI command to block an IP."""
    import sys
    if len(sys.argv) < 3:
        print("Usage: python ip_blocker.py block <ip_address> [reason]")
        sys.exit(1)

    ip = sys.argv[2]
    reason = sys.argv[3] if len(sys.argv) > 3 else "Manual CLI block"
    ip_blocker.block_ip(ip, reason)
    print(f"✅ Blocked {ip}")


def cli_unblock_ip():
    """CLI command to unblock an IP."""
    import sys
    if len(sys.argv) < 3:
        print("Usage: python ip_blocker.py unblock <ip_address>")
        sys.exit(1)

    ip = sys.argv[2]
    ip_blocker.unblock_ip(ip)
    print(f"✅ Unblocked {ip}")


def cli_list_blocked():
    """CLI command to list all blocked IPs."""
    blocked = ip_blocker.get_blocked_ips()
    if blocked:
        print(f"\n🚫 Blocked IPs ({len(blocked)}):")
        for ip in sorted(blocked):
            print(f"  - {ip}")
    else:
        print("\nNo IPs are currently blocked.")


def cli_stats():
    """CLI command to show stats."""
    stats = ip_blocker.get_stats()
    print("\n📊 IP Blocker Statistics:")
    print(f"  Blocked IPs: {stats['blocked_count']}")
    print(f"  Allowed IPs: {stats['allowed_count']}")
    print(f"  Active Violations: {stats['violations_tracked']}")
    print(f"  Auto-block: {'Enabled' if stats['auto_block_enabled'] else 'Disabled'}")
    if stats['auto_block_enabled']:
        print(f"  Auto-block Threshold: {stats['auto_block_threshold']} violations")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("""
IP Blocker Management Tool

Commands:
  block <ip> [reason]    - Block an IP address
  unblock <ip>           - Unblock an IP address
  list                   - List all blocked IPs
  stats                  - Show blocking statistics

Examples:
  python ip_blocker.py block 192.168.1.100 "Bot attack"
  python ip_blocker.py unblock 192.168.1.100
  python ip_blocker.py list
  python ip_blocker.py stats
        """)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'block':
        cli_block_ip()
    elif command == 'unblock':
        cli_unblock_ip()
    elif command == 'list':
        cli_list_blocked()
    elif command == 'stats':
        cli_stats()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

