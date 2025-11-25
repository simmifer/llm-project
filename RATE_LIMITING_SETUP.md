# 🔒 Rate Limiting - Quick Setup

Your app now has rate limiting and admin access! Here's how to set it up:

## ⚡ Quick Start (5 minutes)

### 1. Generate Your Admin Password Hash

```bash
cd llm-project
python rate_limiter.py YourPasswordHere
```

Example:
```bash
python rate_limiter.py MySuperSecret123
```

**Output:**
```
Password: MySuperSecret123
Hash: abc123def456...

Add this to your Streamlit secrets:
ADMIN_PASSWORD_HASH = "abc123def456..."
```

**Save this password somewhere!** You'll need it to access admin mode.

### 2. Update Streamlit Cloud Secrets

Go to: Your App → Settings → Secrets

Add these lines (keep your existing API key):

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."

# New: Rate Limiting
MAX_QUERIES_PER_SESSION = 5
MAX_INPUT_LENGTH = 500
ADMIN_PASSWORD_HASH = "paste-your-hash-here"
```

### 3. Save & Test

Click "Save" → App restarts automatically

**Test as public user:**
- Open app in incognito mode
- Ask 5 questions
- 6th question should be blocked ✅

**Test as admin:**
- Open admin panel in sidebar (🔐 Admin Access)
- Enter your password
- Should see "🔓 Admin Mode Active" ✅
- Unlimited queries!

## 📊 What Users See

### Public Users (Before Limit):
```
ℹ️ Queries remaining this session: 5/5
```

### Public Users (At Limit):
```
🚫 Query limit reached. You've used all 5 queries for this session.

💡 Tip: Refresh the page to start a new session with 5 more queries.
```

### You (Admin Mode):
```
🔓 Admin Mode Active
Unlimited queries enabled
```

## 🎯 Why This Matters

**Without rate limiting:**
- Someone could ask 100 questions = ~$1.50 cost
- Your $5/month limit gets hit fast

**With rate limiting:**
- Max $0.075 per user per session
- Can support 65+ users hitting max queries
- You get unlimited access with password

## 🔧 Adjust Limits

Want to change the limits? Update secrets:

```toml
# More generous (for friends/colleagues)
MAX_QUERIES_PER_SESSION = 10
MAX_INPUT_LENGTH = 1000

# More restrictive (for public)
MAX_QUERIES_PER_SESSION = 3
MAX_INPUT_LENGTH = 300
```

## 📱 When Sharing Your App

**Good message:**
```
Try my ML Concept Explainer: [url]

Note: Limited to 5 queries per session to manage costs.
Refresh page for more queries!
```

This sets expectations and makes limits feel reasonable.

## ✅ Files Updated

New files:
- `rate_limiter.py` - Rate limiting logic
- `RATE_LIMITING.md` - Full documentation

Updated files:
- `app.py` - Integrated rate limiting

## 🚀 Next Steps

1. Generate your password hash
2. Add to Streamlit secrets
3. Test both public and admin modes
4. Share your app with confidence!

Full documentation: See `RATE_LIMITING.md`

---

**Your app is now protected from abuse while staying fully functional!** 🎉