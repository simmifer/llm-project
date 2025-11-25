# Rate Limiting Setup Guide

This guide shows you how to set up rate limiting and admin access for your deployed app.

## Why Rate Limiting?

When sharing your app publicly, you want to:
- **Prevent API cost abuse** - Limit queries so someone can't burn through your API credits
- **Keep admin access** - Bypass limits when you're testing
- **Limit input length** - Prevent excessively long queries that waste tokens

## Features

### For Public Users:
- Limited to **5 queries per session** (configurable)
- Maximum **500 characters per query** (configurable)
- Clear messaging when limits are reached
- Can refresh page to start new session

### For Admin (You):
- **Unlimited queries** with password access
- No character limits
- Session reset button
- See "Admin Mode Active" badge

## Setup Instructions

### Step 1: Generate Admin Password Hash

On your local machine:

```bash
# Navigate to your project
cd llm-project

# Generate password hash
python rate_limiter.py YOUR_PASSWORD
```

Replace `YOUR_PASSWORD` with your actual password (e.g., `MySuperSecretPass123`).

**Output will look like:**
```
Password: MySuperSecretPass123
Hash: 8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918

Add this to your Streamlit secrets:
ADMIN_PASSWORD_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
```

**Important:** Save your password somewhere safe! You'll need it to access admin mode.

### Step 2: Add Secrets to Streamlit Cloud

Go to your app in Streamlit Cloud → Settings → Secrets

Add these lines (keep your existing ANTHROPIC_API_KEY):

```toml
# API Key (you already have this)
ANTHROPIC_API_KEY = "sk-ant-api03-..."

# Rate Limiting Configuration
MAX_QUERIES_PER_SESSION = 5
MAX_INPUT_LENGTH = 500

# Admin Password (use the hash from Step 1)
ADMIN_PASSWORD_HASH = "your-generated-hash-here"
```

**Example with all values:**
```toml
ANTHROPIC_API_KEY = "sk-ant-api03-abc123..."
MAX_QUERIES_PER_SESSION = 5
MAX_INPUT_LENGTH = 500
ADMIN_PASSWORD_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
```

### Step 3: Save and Reboot

Click **"Save"** in Streamlit Cloud. The app will automatically restart with rate limiting enabled.

## Using Admin Mode

### As Admin (You):

1. Open your deployed app
2. Look for **"🔐 Admin Access"** expander in the left sidebar
3. Enter your password
4. Click **"Login"**
5. You'll see **"🔓 Admin Mode Active"** badge
6. Now you have unlimited queries!

### As Public User:

- They see: **"ℹ️ Queries remaining this session: 5/5"**
- After 5 queries: **"🚫 Query limit reached"**
- Message prompts them to refresh page for new session

## Customizing Limits

You can adjust the limits in Streamlit Cloud secrets:

### More/Fewer Queries:
```toml
MAX_QUERIES_PER_SESSION = 10  # Allow 10 queries instead of 5
```

### Longer/Shorter Questions:
```toml
MAX_INPUT_LENGTH = 300  # Allow only 300 characters (saves tokens)
MAX_INPUT_LENGTH = 1000  # Allow longer questions
```

Changes take effect immediately after saving secrets (app auto-restarts).

## How It Works

### Session-Based Tracking:
- Each user gets a fresh session when they open the app
- Session persists while browser tab is open
- Refreshing page = new session with fresh query count

### Security:
- Password is hashed with SHA-256
- Only the hash is stored in secrets (not plain password)
- Admin status stored in Streamlit session (not shareable)

### What's Tracked:
- Number of queries in current session
- Whether user is admin
- Session start time

### What's NOT Tracked:
- User identity
- IP addresses
- Query history (except in your logs)

## Testing

### Test Public Access:
1. Open app in incognito window
2. Ask 5 questions
3. Try to ask a 6th - should be blocked
4. Refresh page - should work again

### Test Admin Access:
1. Open admin panel in sidebar
2. Enter your password
3. Verify unlimited access works
4. Test session reset button

## Troubleshooting

### "Admin Access" panel doesn't appear:
- Check that `ADMIN_PASSWORD_HASH` is in Streamlit secrets
- Make sure there are no extra quotes or spaces

### Can't login as admin:
- Verify you're using the correct password
- Regenerate hash: `python rate_limiter.py YOUR_PASSWORD`
- Copy the hash exactly (no spaces before/after)

### Rate limiting not working:
- Check `MAX_QUERIES_PER_SESSION` is set in secrets
- Try refreshing the Streamlit app
- Check app logs for errors

### Users complaining they can't ask questions:
- They've hit their limit - tell them to refresh page
- Or increase `MAX_QUERIES_PER_SESSION` in secrets

## Cost Estimates

With these limits, worst case per user:
- 5 queries × ~2,500 tokens input × $3/M = $0.0375
- 5 queries × ~500 tokens output × $15/M = $0.0375
- **Total per user: ~$0.075 max**

With your $5/month limit:
- You can support ~65 users hitting max queries
- Or hundreds of casual users (1-2 queries each)

## Recommended Settings

### For Public Demo:
```toml
MAX_QUERIES_PER_SESSION = 5
MAX_INPUT_LENGTH = 500
```

### For Internal Team:
```toml
MAX_QUERIES_PER_SESSION = 20
MAX_INPUT_LENGTH = 1000
```

### For Portfolio (Low Traffic):
```toml
MAX_QUERIES_PER_SESSION = 3
MAX_INPUT_LENGTH = 300
```

## Advanced: Monitoring Usage

Your query logger (`view_logs.py`) tracks all queries, even from public users.

After people use your app:
```bash
# See total usage
python view_logs.py stats

# See recent queries
python view_logs.py recent 20
```

This shows you:
- How many people are using it
- What questions they're asking
- Total costs

**Note:** Logs reset on Streamlit Cloud when app redeploys, so download them periodically if you want to keep them.

## Sharing Best Practices

When sharing your app:

**Good:**
```
Check out my RAG system demo: [url]

Note: Limited to 5 queries per session to manage API costs.
Refresh page for more queries!
```

**Even Better:**
```
Try my ML Concept Explainer: [url]

Ask about embeddings, RAG, or fine-tuning!
(Limited to 5 free queries - refresh for more)

Want unlimited access? DM me for the password.
```

This sets expectations and makes the limits feel reasonable.

## Questions?

If you need to:
- Change your admin password: regenerate hash and update secrets
- Remove rate limiting: remove the limits from app.py
- Track users better: add analytics or persistent logging

See `ENHANCEMENTS.md` for ideas on more sophisticated rate limiting (IP-based, tiered access, etc.).

---

**Your app is now protected from API abuse while still being fully accessible to testers!** 🎉