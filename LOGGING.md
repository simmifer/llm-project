# Query Logging System

The ML Concept Explainer includes automatic logging of all queries, responses, and token usage.

## What Gets Logged

Every query automatically logs:
- Query text
- Generated answer
- Sources retrieved (with similarity scores)
- Token usage (input, output, total)
- Timestamp
- Model used
- Estimated cost (USD)

## Storage

Logs are stored in a SQLite database (`query_logs.db`) for easy querying and analysis.

## Viewing Logs

### Interactive Menu
```bash
python view_logs.py
```

This opens an interactive menu where you can:
- View aggregate statistics
- See recent queries
- View detailed query information
- Export logs to JSON

### Command Line

**View statistics:**
```bash
python view_logs.py stats
```

Output:
```
QUERY LOG STATISTICS
====================================================================
Total queries: 5
Token Usage:
  Total tokens: 12,450
  Input tokens: 10,200
  Output tokens: 2,250
Cost Analysis:
  Total cost: $0.0642
  Average cost per query: $0.0128
Averages per query:
  Input tokens: 2040
  Output tokens: 450
  Chunks retrieved: 3.0
====================================================================
```

**View recent queries:**
```bash
python view_logs.py recent 5
```

**View specific query:**
```bash
python view_logs.py details 3
```

**Export to JSON:**
```bash
python view_logs.py export
```

## Programmatic Access

You can also access logs programmatically:

```python
from query_logger import QueryLogger

logger = QueryLogger()

# Get all queries
queries = logger.get_all_queries()

# Get statistics
stats = logger.get_stats()
print(f"Total cost: ${stats['total_cost']:.4f}")

# Export to JSON
logger.export_to_json("my_logs.json")
```

## Cost Tracking

The logger automatically calculates estimated costs based on Claude Sonnet 4 pricing:
- Input tokens: $3 per million tokens
- Output tokens: $15 per million tokens

Example cost breakdown:
```
Query with 2,000 input tokens and 500 output tokens:
  Input cost: 2,000 / 1,000,000 × $3 = $0.006
  Output cost: 500 / 1,000,000 × $15 = $0.0075
  Total: $0.0135
```

## Usage Analysis

### Track Optimization Impact

Compare token usage before and after optimization:

```bash
# Before optimization
python view_logs.py stats
> Average input tokens: 3500

# After optimization (e.g., reducing chunks from 5 to 3)
python view_logs.py stats
> Average input tokens: 2100
> Savings: 40% reduction in input tokens
```

### Cost Monitoring

```bash
# View cumulative costs
python view_logs.py stats
> Total cost: $0.0642

# Export for spreadsheet analysis
python view_logs.py export
# Then analyze query_logs.json in Excel/Google Sheets
```

### Query Pattern Analysis

```python
from query_logger import QueryLogger

logger = QueryLogger()
queries = logger.get_all_queries()

# Find most expensive queries
expensive = sorted(queries, key=lambda q: q['total_tokens'], reverse=True)[:5]
for q in expensive:
    print(f"{q['query'][:50]}: {q['total_tokens']} tokens")

# Find queries with low similarity scores
low_similarity = [q for q in queries 
                  if any(s['similarity'] < 0.3 for s in q['sources'])]
print(f"Queries with low-relevance sources: {len(low_similarity)}")
```

## Privacy Note

The database contains your queries and Claude's responses. 

- **Stored locally** in `query_logs.db`
- **Not pushed to GitHub** (in `.gitignore`)
- **Backup recommended** if you want to preserve logs

To backup:
```bash
# Backup database
cp query_logs.db query_logs_backup.db

# Or export to JSON
python view_logs.py export
```

## Disabling Logging

To disable logging (not recommended for learning purposes):

```python
# In rag_system.py or when initializing:
rag = RAGSystem(store, enable_logging=False)
```

Or in `app.py`:
```python
st.session_state.rag_system = RAGSystem(store, enable_logging=False)
```

## Database Schema

```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    query TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources TEXT NOT NULL,          -- JSON array
    chunks_retrieved INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    model TEXT,
    cost_estimate_usd REAL
);
```

## Advanced: SQL Queries

You can query the database directly with SQLite:

```bash
sqlite3 query_logs.db

# Average tokens by date
SELECT 
    DATE(timestamp) as date,
    AVG(input_tokens) as avg_input,
    AVG(output_tokens) as avg_output,
    COUNT(*) as queries
FROM queries
GROUP BY DATE(timestamp);

# Most expensive queries
SELECT query, total_tokens, cost_estimate_usd
FROM queries
ORDER BY cost_estimate_usd DESC
LIMIT 5;

# Token usage over time
SELECT 
    strftime('%Y-%m-%d %H:00', timestamp) as hour,
    SUM(total_tokens) as tokens
FROM queries
GROUP BY hour;
```

## Example Analysis Session

```bash
# Run some queries through the app
streamlit run app.py
# (Ask 5-10 questions)

# View statistics
python view_logs.py stats

# See what you asked
python view_logs.py recent 10

# Export for detailed analysis
python view_logs.py export

# Open in Python for custom analysis
python
>>> from query_logger import QueryLogger
>>> logger = QueryLogger()
>>> queries = logger.get_all_queries()
>>> avg_cost = sum(q['cost_estimate_usd'] for q in queries) / len(queries)
>>> print(f"Average query cost: ${avg_cost:.4f}")
```

## Logging in Production

This logging system demonstrates:
- **Cost tracking** - Critical for production LLM apps
- **Usage analytics** - Understanding user patterns
- **Performance monitoring** - Identifying optimization opportunities
- **Debugging** - Seeing what queries work/fail
- **Compliance** - Audit trail of AI interactions

This is a simplified version. Production systems would add:
- User IDs and session tracking
- Error logging
- Latency metrics
- A/B test tracking
- More sophisticated cost allocation