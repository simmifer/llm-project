# 🎯 Logging System Added!

I've added a complete query logging and analytics system to your ML Concept Explainer.

## What Was Added

### New Files
1. **query_logger.py** - Core logging system using SQLite
2. **view_logs.py** - Log viewer and analytics tool
3. **LOGGING.md** - Complete documentation
4. **.gitignore** - Updated to exclude log files

### Modified Files
1. **rag_system.py** - Now captures and logs token usage
2. **app.py** - Displays token usage metrics in the UI

## What Gets Logged Automatically

Every query now logs:
- ✅ Query text
- ✅ Answer text
- ✅ Sources retrieved (with similarity scores)
- ✅ Input tokens
- ✅ Output tokens
- ✅ Estimated cost (USD)
- ✅ Timestamp
- ✅ Model used

## How to Use

### In the UI
Tokens and cost now display automatically after each answer:
```
Input Tokens: 2,134
Output Tokens: 567
Cost: $0.0149
```

### View Your Logs

**Interactive menu:**
```bash
python view_logs.py
```

**Quick stats:**
```bash
python view_logs.py stats
```

**Recent queries:**
```bash
python view_logs.py recent 10
```

**Export everything:**
```bash
python view_logs.py export
# Creates query_logs.json
```

## Example Output

After asking a few questions, run:
```bash
python view_logs.py stats
```

You'll see:
```
QUERY LOG STATISTICS
====================================================================
Total queries: 8
Token Usage:
  Total tokens: 19,234
  Input tokens: 15,890
  Output tokens: 3,344
Cost Analysis:
  Total cost: $0.0978
  Average cost per query: $0.0122
Averages per query:
  Input tokens: 1986
  Output tokens: 418
  Chunks retrieved: 3.0
====================================================================
```

## Why This Matters

This demonstrates **production-level thinking**:

1. **Cost Management** - Track spend on LLM APIs
2. **Optimization** - See impact of changes (e.g., 5 chunks → 3 chunks)
3. **Analytics** - Understand usage patterns
4. **Debugging** - See exactly what went into each query
5. **Compliance** - Audit trail for AI interactions

## For Your Portfolio

This shows you understand:
- **Production concerns** (cost tracking isn't an afterthought)
- **Data management** (SQLite for structured logging)
- **User analytics** (measuring what matters)
- **Engineering maturity** (logging from day 1)

## Database Schema

Simple SQLite database with one table:
```
queries
  ├── id (primary key)
  ├── timestamp
  ├── query
  ├── answer
  ├── sources (JSON)
  ├── chunks_retrieved
  ├── input_tokens
  ├── output_tokens
  ├── total_tokens
  ├── model
  └── cost_estimate_usd
```

## Privacy Note

- Logs stored locally in `query_logs.db`
- NOT pushed to GitHub (in `.gitignore`)
- You own your data

## Quick Test

```bash
# 1. Ask a question in the UI
streamlit run app.py
# Ask: "What are embeddings?"

# 2. View the log
python view_logs.py recent 1
```

You'll see the full query, answer, tokens, and cost!

## Advanced Analysis

You can query the database directly:
```bash
sqlite3 query_logs.db

SELECT query, total_tokens, cost_estimate_usd 
FROM queries 
ORDER BY cost_estimate_usd DESC 
LIMIT 5;
```

Or use Python:
```python
from query_logger import QueryLogger

logger = QueryLogger()
queries = logger.get_all_queries()

# Find most expensive queries
expensive = sorted(queries, key=lambda q: q['total_tokens'], reverse=True)
for q in expensive[:3]:
    print(f"{q['query']}: ${q['cost_estimate_usd']:.4f}")
```

## Update Your Local Files

The updated files are in `/mnt/user-data/outputs/ml-concept-explainer/`:
- query_logger.py (NEW)
- view_logs.py (NEW)
- LOGGING.md (NEW)
- .gitignore (UPDATED)
- rag_system.py (UPDATED)
- app.py (UPDATED)

Copy them to your local repo and you're ready to go!

## To Test

```bash
# Start the app
streamlit run app.py

# Ask some questions

# View your logs
python view_logs.py stats

# See details
python view_logs.py recent 5
```

---

**This is exactly the kind of instrumentation production ML systems need.** You're not just building a demo - you're building something you can actually learn from and optimize. 🚀