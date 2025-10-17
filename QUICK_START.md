# 🚨 Quick Start: Secure Your OpenAI API Now

## What's The Problem?

**YES, your Flask app can drain your OpenAI credits** if exposed without protection. Every search query calls OpenAI, and bots can make thousands of requests per hour.

## ✅ What We Fixed

I've added comprehensive security to protect you:

1. ✅ **Rate Limiting** - Max 10 requests/min per user
2. ✅ **API Authentication** - Requires API key to access
3. ✅ **Budget Protection** - Auto-reject when limits exceeded
4. ✅ **IP Blocking** - Block malicious IPs automatically
5. ✅ **Usage Monitoring** - Track costs and detect abuse
6. ✅ **Request Logging** - Full audit trail in `api_usage.log`

## 🚀 Setup in 5 Minutes

### Step 1: Create Environment File (2 min)
```bash
cd /Users/abierschenk/Desktop/tableau_langchain

# Copy the template
cp env.example .env

# Generate secure API keys
python -c "import secrets; print('API Key 1:', secrets.token_urlsafe(32)); print('API Key 2:', secrets.token_urlsafe(32))"
```

### Step 2: Edit .env File (2 min)
```bash
nano .env  # or use your preferred editor
```

**Required settings:**
```bash
# Your OpenAI key (REQUIRED)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# App API keys - use the keys generated in Step 1
ALLOWED_API_KEYS=paste-key1-here,paste-key2-here

# Rate limits (start conservative)
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
RATE_LIMIT_PER_DAY=1000

# Budget protection
HOURLY_BUDGET_USD=2.0
DAILY_BUDGET_USD=10.0
```

### Step 3: Set OpenAI Spending Limits (1 min)
1. Go to: https://platform.openai.com/account/billing/limits
2. Set **Hard limit**: $50/month (or whatever you're comfortable with)
3. Set **Soft limit**: $25/month (for email alerts)

### Step 4: Restart Your App
```bash
# Kill any running instances
pkill -f "rag_demo_flask"

# Start with security enabled
cd experimental/demos
python rag_demo_flask.py
```

You should see:
```
🚀 Tableau LangChain RAG Demo - SECURED
Security features enabled:
  ✅ API Authentication: ENABLED
  ✅ Rate Limiting: 10/min
  ✅ Budget Protection: $2.0/hour, $10.0/day
  ✅ IP Blocking: 0 IPs blocked
  ✅ Request Logging: api_usage.log
```

## 📊 Monitor Your Usage

### Real-time monitoring:
```bash
# Watch logs as they happen
tail -f api_usage.log

# Check usage stats
python experimental/utilities/monitor_usage.py

# Check with alerts
python experimental/utilities/monitor_usage.py --alert
```

### Test the security:
```bash
# Run the test suite
./test_security.sh
```

## 🔒 How to Use Your API Now

With security enabled, all requests need an API key:

```bash
# Old way (now blocked):
curl -X POST http://localhost:5000/search -F "query=test"
# Response: 401 Unauthorized ✅

# New way (required):
curl -X POST http://localhost:5000/search \
  -H "X-API-Key: your-api-key-from-env" \
  -F "query=test"
# Response: 200 OK with results ✅
```

## 📁 Important Files Created

| File | Purpose |
|------|---------|
| `env.example` | Template for environment variables |
| `SECURITY_SETUP.md` | Detailed security documentation |
| `URGENT_COST_ANALYSIS.md` | **READ THIS** - explains the cost issues |
| `experimental/utilities/security.py` | Core security module |
| `experimental/utilities/ip_blocker.py` | IP blocking system |
| `experimental/utilities/monitor_usage.py` | Usage monitoring tool |
| `test_security.sh` | Security test suite |

## ⚠️ Critical: Read This

**URGENT_COST_ANALYSIS.md** explains:
- ✅ What was costing you money
- ✅ How much it could have cost (worst case: $84K/month!)
- ✅ What we fixed
- ✅ How to check your current damage
- ✅ What to do if you're already over budget

## 🆘 Emergency: If You're Already Over Budget

```bash
# 1. STOP ALL APPLICATIONS
pkill -f python

# 2. Rotate OpenAI key immediately
#    → https://platform.openai.com/api-keys
#    → Delete old key, generate new one

# 3. Update .env with new key
nano .env

# 4. Check your usage
#    → https://platform.openai.com/usage

# 5. Contact OpenAI support
#    → support@openai.com
#    → Explain bot abuse, request refund
```

## ✅ Production Deployment Checklist

Before going live:

- [ ] `.env` configured with strong API keys
- [ ] `ALLOWED_API_KEYS` is NOT empty
- [ ] OpenAI hard spending limit set
- [ ] HTTPS enabled (nginx/Cloudflare)
- [ ] Monitoring script running
- [ ] Tested with `./test_security.sh`
- [ ] Read `SECURITY_SETUP.md` fully
- [ ] Read `URGENT_COST_ANALYSIS.md` fully
- [ ] Log rotation configured
- [ ] Backup strategy for logs

## 📚 Documentation

- **URGENT_COST_ANALYSIS.md** - Understanding the cost issues ⚠️ READ FIRST
- **SECURITY_SETUP.md** - Complete security guide
- **env.example** - Configuration template

## 🎯 Quick Commands

```bash
# Monitor usage
python experimental/utilities/monitor_usage.py

# Check logs
tail -f api_usage.log

# Block an IP
python experimental/utilities/ip_blocker.py block 1.2.3.4 "Bot attack"

# Unblock an IP
python experimental/utilities/ip_blocker.py unblock 1.2.3.4

# List blocked IPs
python experimental/utilities/ip_blocker.py list

# Test security
./test_security.sh
```

## ✨ You're Now Protected!

The security is in place. Just need to:
1. Configure `.env` (2 min)
2. Set OpenAI limits (1 min)
3. Restart your app
4. Monitor for 24 hours

**Sleep better knowing your API is protected!** 🛡️😴

