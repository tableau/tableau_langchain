#!/usr/bin/env python3
"""
Usage Monitoring and Alerting Script

Run this script periodically to monitor API usage and costs.
Can be scheduled with cron or run manually.

Usage:
    python monitor_usage.py                    # Show current usage
    python monitor_usage.py --json             # Output as JSON
    python monitor_usage.py --alert            # Send alerts if thresholds exceeded
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def parse_log_file(log_path='api_usage.log'):
    """Parse usage log file and extract statistics."""

    if not os.path.exists(log_path):
        return {
            'error': f'Log file not found: {log_path}',
            'requests': [],
            'usage': {}
        }

    requests = []
    usage_by_user = defaultdict(lambda: {
        'requests': 0,
        'tokens': 0,
        'cost': 0.0,
        'models': set()
    })

    with open(log_path, 'r') as f:
        for line in f:
            # Parse request lines
            if 'Request:' in line:
                parts = line.split(' - ')
                if len(parts) >= 3:
                    timestamp = parts[0]
                    message = parts[-1].strip()
                    requests.append({
                        'timestamp': timestamp,
                        'message': message
                    })

            # Parse usage tracking lines
            if 'Usage tracked' in line:
                try:
                    # Example: "Usage tracked - ID: abc123, Model: gpt-4o-mini, Tokens: 100+50, Cost: $0.0001"
                    if 'ID:' in line and 'Model:' in line and 'Tokens:' in line and 'Cost:' in line:
                        user_id = line.split('ID: ')[1].split(',')[0].strip()
                        model = line.split('Model: ')[1].split(',')[0].strip()
                        tokens_str = line.split('Tokens: ')[1].split(',')[0].strip()
                        cost_str = line.split('Cost: $')[1].strip()

                        # Parse tokens (format: "100+50")
                        if '+' in tokens_str:
                            input_tokens, output_tokens = map(int, tokens_str.split('+'))
                            total_tokens = input_tokens + output_tokens
                        else:
                            total_tokens = int(tokens_str)

                        cost = float(cost_str)

                        usage_by_user[user_id]['requests'] += 1
                        usage_by_user[user_id]['tokens'] += total_tokens
                        usage_by_user[user_id]['cost'] += cost
                        usage_by_user[user_id]['models'].add(model)
                except Exception as e:
                    # Skip malformed lines
                    continue

    # Convert sets to lists for JSON serialization
    for user_data in usage_by_user.values():
        user_data['models'] = list(user_data['models'])

    return {
        'total_requests': len(requests),
        'usage_by_user': dict(usage_by_user),
        'last_updated': datetime.now().isoformat()
    }


def calculate_time_based_stats(log_path='api_usage.log', hours=24):
    """Calculate statistics for a specific time window."""

    cutoff_time = datetime.now() - timedelta(hours=hours)

    total_cost = 0.0
    total_tokens = 0
    total_requests = 0
    errors = 0
    rate_limit_violations = 0
    budget_violations = 0

    if not os.path.exists(log_path):
        return None

    with open(log_path, 'r') as f:
        for line in f:
            try:
                # Parse timestamp
                timestamp_str = line.split(' - ')[0]
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')

                if timestamp < cutoff_time:
                    continue

                # Count different event types
                if 'Request:' in line:
                    total_requests += 1

                if 'ERROR' in line:
                    errors += 1

                if 'Rate limit exceeded' in line:
                    rate_limit_violations += 1

                if 'budget exceeded' in line:
                    budget_violations += 1

                if 'Usage tracked' in line and 'Cost:' in line:
                    cost_str = line.split('Cost: $')[1].strip()
                    total_cost += float(cost_str)

                    if 'Tokens:' in line:
                        tokens_str = line.split('Tokens: ')[1].split(',')[0].strip()
                        if '+' in tokens_str:
                            input_t, output_t = map(int, tokens_str.split('+'))
                            total_tokens += input_t + output_t
                        else:
                            total_tokens += int(tokens_str)

            except Exception:
                continue

    return {
        'time_window_hours': hours,
        'total_requests': total_requests,
        'total_tokens': total_tokens,
        'total_cost_usd': round(total_cost, 4),
        'errors': errors,
        'rate_limit_violations': rate_limit_violations,
        'budget_violations': budget_violations,
        'average_cost_per_request': round(total_cost / max(total_requests, 1), 6)
    }


def check_alerts(stats, hourly_budget=None, daily_budget=None):
    """Check if usage exceeds alert thresholds."""

    alerts = []

    if hourly_budget:
        hourly_stats = stats.get('hourly')
        if hourly_stats and hourly_stats['total_cost_usd'] >= hourly_budget * 0.8:
            alerts.append({
                'severity': 'WARNING',
                'message': f"Approaching hourly budget: ${hourly_stats['total_cost_usd']:.4f} / ${hourly_budget}"
            })
        if hourly_stats and hourly_stats['total_cost_usd'] >= hourly_budget:
            alerts.append({
                'severity': 'CRITICAL',
                'message': f"Hourly budget exceeded: ${hourly_stats['total_cost_usd']:.4f} / ${hourly_budget}"
            })

    if daily_budget:
        daily_stats = stats.get('daily')
        if daily_stats and daily_stats['total_cost_usd'] >= daily_budget * 0.8:
            alerts.append({
                'severity': 'WARNING',
                'message': f"Approaching daily budget: ${daily_stats['total_cost_usd']:.4f} / ${daily_budget}"
            })
        if daily_stats and daily_stats['total_cost_usd'] >= daily_budget:
            alerts.append({
                'severity': 'CRITICAL',
                'message': f"Daily budget exceeded: ${daily_stats['total_cost_usd']:.4f} / ${daily_budget}"
            })

    # Check for anomalies
    hourly_stats = stats.get('hourly', {})
    if hourly_stats.get('rate_limit_violations', 0) > 10:
        alerts.append({
            'severity': 'WARNING',
            'message': f"High rate limit violations: {hourly_stats['rate_limit_violations']} in last hour"
        })

    if hourly_stats.get('errors', 0) > 50:
        alerts.append({
            'severity': 'WARNING',
            'message': f"High error rate: {hourly_stats['errors']} errors in last hour"
        })

    return alerts


def main():
    parser = argparse.ArgumentParser(description='Monitor OpenAI API usage and costs')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--alert', action='store_true', help='Check for alerts')
    parser.add_argument('--log-file', default='api_usage.log', help='Path to log file')
    args = parser.parse_args()

    # Load environment for budget limits
    from dotenv import load_dotenv
    load_dotenv()

    hourly_budget = float(os.getenv('HOURLY_BUDGET_USD', '2.0'))
    daily_budget = float(os.getenv('DAILY_BUDGET_USD', '10.0'))

    # Get statistics
    overall_stats = parse_log_file(args.log_file)
    hourly_stats = calculate_time_based_stats(args.log_file, hours=1)
    daily_stats = calculate_time_based_stats(args.log_file, hours=24)

    stats = {
        'overall': overall_stats,
        'hourly': hourly_stats,
        'daily': daily_stats,
        'budget_limits': {
            'hourly_usd': hourly_budget,
            'daily_usd': daily_budget
        }
    }

    if args.alert:
        alerts = check_alerts(stats, hourly_budget, daily_budget)
        stats['alerts'] = alerts

        if alerts:
            print("\n🚨 ALERTS DETECTED 🚨\n")
            for alert in alerts:
                symbol = "⚠️ " if alert['severity'] == 'WARNING' else "🔴"
                print(f"{symbol} [{alert['severity']}] {alert['message']}")
            print()

    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        # Human-readable output
        print("\n" + "="*60)
        print("OpenAI API Usage Report")
        print("="*60)

        print(f"\n📊 Overall Statistics:")
        print(f"   Total Requests: {overall_stats.get('total_requests', 0)}")
        print(f"   Unique Users: {len(overall_stats.get('usage_by_user', {}))}")

        if hourly_stats:
            print(f"\n⏰ Last Hour:")
            print(f"   Requests: {hourly_stats['total_requests']}")
            print(f"   Tokens: {hourly_stats['total_tokens']:,}")
            print(f"   Cost: ${hourly_stats['total_cost_usd']:.4f} / ${hourly_budget} (budget)")
            print(f"   Errors: {hourly_stats['errors']}")
            print(f"   Rate Limits Hit: {hourly_stats['rate_limit_violations']}")

        if daily_stats:
            print(f"\n📅 Last 24 Hours:")
            print(f"   Requests: {daily_stats['total_requests']}")
            print(f"   Tokens: {daily_stats['total_tokens']:,}")
            print(f"   Cost: ${daily_stats['total_cost_usd']:.4f} / ${daily_budget} (budget)")
            print(f"   Avg Cost/Request: ${daily_stats['average_cost_per_request']:.6f}")
            print(f"   Errors: {daily_stats['errors']}")
            print(f"   Rate Limits Hit: {daily_stats['rate_limit_violations']}")

        print(f"\n💰 Budget Status:")
        if hourly_stats:
            hourly_pct = (hourly_stats['total_cost_usd'] / hourly_budget * 100)
            print(f"   Hourly: {hourly_pct:.1f}% used")
        if daily_stats:
            daily_pct = (daily_stats['total_cost_usd'] / daily_budget * 100)
            print(f"   Daily: {daily_pct:.1f}% used")

        print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()

