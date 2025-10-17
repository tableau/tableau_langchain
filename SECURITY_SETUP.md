# 🔒 Security Setup Guide - Protecting Your OpenAI Credits

This guide will help you implement critical security measures to prevent bots and unauthorized users from draining your OpenAI API credits.

## ⚠️ URGENT: Immediate Actions Required

If your application is currently running in production without security measures:

1. **Stop the application immediately** if you suspect abuse
2. **Check your OpenAI usage dashboard**: https://platform.openai.com/usage
3. **Rotate your API keys** at https://platform.openai.com/api-keys
4. **Set spending limits** in your OpenAI account settings
5. Follow the setup instructions below before restarting

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Security Features](#security-features)
- [Configuration](#configuration)
- [Deployment Checklist](#deployment-checklist)
- [Monitoring & Alerts](#monitoring--alerts)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### 1. Copy Environment Template

```bash
cp env.example .env
```

### 2. Generate Strong API Keys

Generate secure API keys for your application:

```bash
python -c "import secrets; print(f'Key 1: {secrets.token_urlsafe(32)}'); print(f'Key 2: {secrets.token_urlsafe(32)}'); print(f'Key 3: {secrets.token_urlsafe(32)}')"
```

### 3. Configure .env File

Edit `.env` with your settings:

```bash
# CRITICAL: Set these values
OPENAI_API_KEY=sk-your-actual-openai-key

# Application API Keys (comma-separated)
ALLOWED_API_KEYS=key1_from_step2,key2_from_step2,key3_from_step2

# Rate Limits (adjust based on your needs)
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
RATE_LIMIT_PER_DAY=1000

# Budget Limits (USD)
HOURLY_BUDGET_USD=2.0
DAILY_BUDGET_USD=10.0
```

### 4. Verify Security Configuration

Run the validation check:

```bash
python -c "from experimental.utilities.security import validate_environment; validate_environment()"
```

You should see:
```
✅ Environment validation passed
Security Status:
  - API Authentication: ENABLED
  - Rate Limiting: 10/min, 100/hour
  - Budget Limits: $2.0/hour, $10.0/day
```

### 5. Test the Protected Endpoint

With authentication enabled, all API requests require the `X-API-Key` header:

```bash
# This will fail (no API key)
curl -X POST http://localhost:5000/search \
  -F "query=test"

# This will succeed (with API key)
curl -X POST http://localhost:5000/search \
  -H "X-API-Key: your-generated-key-from-step2" \
  -F "query=test"
```

## 🛡️ Security Features

### 1. API Key Authentication
- Whitelist-based authentication
- All API endpoints require valid API key in `X-API-Key` header
- Keys are hashed for rate limiting (never logged in plaintext)

### 2. Rate Limiting
- **Per-minute limits**: Prevents rapid-fire bot attacks
- **Per-hour limits**: Prevents sustained abuse
- **Per-day limits**: Overall usage cap
- Tracks separately per IP address and API key

### 3. Budget Protection
- **Hourly budget**: Default $2/hour
- **Daily budget**: Default $10/day
- Automatic cost estimation based on model and token usage
- Requests rejected when budget exceeded

### 4. Request Logging
- All API requests logged with timestamps
- IP addresses, API keys (hashed), and response times tracked
- Usage statistics for monitoring and debugging
- Logs saved to `api_usage.log`

### 5. Input Validation
- Query length limits (max 500 characters)
- Request size validation
- Malformed request rejection

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | Your OpenAI API key |
| `ALLOWED_API_KEYS` | ⚠️ Recommended | Empty | Comma-separated list of allowed keys |
| `RATE_LIMIT_PER_MINUTE` | No | 10 | Max requests per minute |
| `RATE_LIMIT_PER_HOUR` | No | 100 | Max requests per hour |
| `RATE_LIMIT_PER_DAY` | No | 1000 | Max requests per day |
| `HOURLY_BUDGET_USD` | No | 2.0 | Max spend per hour (USD) |
| `DAILY_BUDGET_USD` | No | 10.0 | Max spend per day (USD) |

### Adjusting Rate Limits

Start conservative and increase as needed:

**For Internal Use (Small Team):**
```bash
RATE_LIMIT_PER_MINUTE=5
RATE_LIMIT_PER_HOUR=50
RATE_LIMIT_PER_DAY=200
HOURLY_BUDGET_USD=1.0
DAILY_BUDGET_USD=5.0
```

**For Production (Public Access):**
```bash
RATE_LIMIT_PER_MINUTE=20
RATE_LIMIT_PER_HOUR=200
RATE_LIMIT_PER_DAY=2000
HOURLY_BUDGET_USD=5.0
DAILY_BUDGET_USD=50.0
```

**For High-Traffic Applications:**
```bash
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000
HOURLY_BUDGET_USD=20.0
DAILY_BUDGET_USD=200.0
```

## ✅ Deployment Checklist

Before deploying to production:

- [ ] `.env` file created and configured (never commit this!)
- [ ] `ALLOWED_API_KEYS` set with strong, random keys
- [ ] Rate limits configured appropriately for your use case
- [ ] Budget limits set to protect against overuse
- [ ] Security validation passes: `validate_environment()`
- [ ] HTTPS enabled (use reverse proxy like nginx or Cloudflare)
- [ ] Log monitoring set up: `tail -f api_usage.log`
- [ ] OpenAI dashboard spending limits configured
- [ ] API keys distributed securely to authorized users only
- [ ] `.gitignore` includes `.env` and `*.log` files
- [ ] Backup/monitoring system for `api_usage.log`

## 📊 Monitoring & Alerts

### 1. Real-Time Log Monitoring

Monitor requests in real-time:

```bash
# Watch all activity
tail -f api_usage.log

# Filter for errors
tail -f api_usage.log | grep ERROR

# Filter for rate limit violations
tail -f api_usage.log | grep "Rate limit exceeded"

# Filter for budget violations
tail -f api_usage.log | grep "budget exceeded"
```

### 2. Usage Analysis

Analyze your logs:

```bash
# Count requests by hour
cat api_usage.log | grep "Request:" | cut -d' ' -f1-2 | uniq -c

# Find most active IPs
cat api_usage.log | grep "Request:" | grep -oE '\d+\.\d+\.\d+\.\d+' | sort | uniq -c | sort -rn | head -10

# Check for failed authentications
cat api_usage.log | grep "Authentication failed"
```

### 3. Cost Monitoring Script

Create a simple monitoring script:

```python
# monitor_costs.py
from experimental.utilities.security import usage_tracker

# Get all tracked users
for identifier, entries in usage_tracker.usage_log.items():
    if entries:
        total_cost = sum(e['cost'] for e in entries)
        total_tokens = sum(e['input_tokens'] + e['output_tokens'] for e in entries)
        print(f"User {identifier[:8]}... - Cost: ${total_cost:.4f}, Tokens: {total_tokens}")
```

### 4. Set Up Alerts

For production, set up automated alerts:

```bash
# Simple email alert on budget warning (add to crontab)
*/30 * * * * /path/to/check_usage.sh
```

Example `check_usage.sh`:
```bash
#!/bin/bash
THRESHOLD=0.80
CURRENT=$(python -c "from experimental.utilities.security import usage_tracker; print(sum(sum(e['cost'] for e in entries) for entries in usage_tracker.usage_log.values()))")

# Add email alert logic here
```

## 🚨 What to Do If You're Under Attack

### Immediate Actions:

1. **Stop the application**
   ```bash
   pkill -f flask  # or your application process
   ```

2. **Rotate OpenAI API key**
   - Go to https://platform.openai.com/api-keys
   - Revoke current key
   - Generate new key
   - Update `.env` file

3. **Review logs for attack patterns**
   ```bash
   cat api_usage.log | grep -A 2 "Rate limit exceeded"
   ```

4. **Block malicious IPs** (if using nginx/apache)
   ```nginx
   # In nginx.conf
   deny 1.2.3.4;  # Replace with actual IP
   ```

5. **Temporarily disable API access**
   ```bash
   # In .env - remove all allowed keys
   ALLOWED_API_KEYS=
   # This will block ALL access
   ```

6. **Contact OpenAI support**
   - Report the incident
   - Request usage review
   - Potentially request credit refund for fraudulent usage

## 🔧 Troubleshooting

### "Environment validation failed"

Check that your `.env` file exists and contains `OPENAI_API_KEY`:
```bash
cat .env | grep OPENAI_API_KEY
```

### "API authentication is DISABLED"

You haven't set `ALLOWED_API_KEYS`. This is okay for development but **NOT for production**:
```bash
echo "ALLOWED_API_KEYS=your_generated_key_here" >> .env
```

### "Rate limit exceeded" errors for legitimate users

Increase rate limits in `.env`:
```bash
RATE_LIMIT_PER_MINUTE=20  # Increase from 10
```

### Log file getting too large

Set up log rotation:
```bash
# Create /etc/logrotate.d/tableau-langchain
/path/to/api_usage.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## 📚 Additional Resources

- [OpenAI Usage Dashboard](https://platform.openai.com/usage)
- [OpenAI Rate Limits Documentation](https://platform.openai.com/docs/guides/rate-limits)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)

## 🆘 Support

If you need help:
1. Check `api_usage.log` for detailed error messages
2. Review this security guide thoroughly
3. Check OpenAI dashboard for usage patterns
4. Review rate limit and budget configurations

---

**Remember:** Security is not a one-time setup. Regularly monitor your logs, review your OpenAI usage, and adjust limits as your application grows.

**Stay safe! 🔒**

