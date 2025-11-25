"""
Query Logger Module

Logs all queries, responses, and token usage to a SQLite database.
Allows post-facto analysis of usage patterns and costs.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os


class QueryLogger:
    """
    Logs RAG queries and responses to SQLite database.
    
    Tracks:
    - Query text
    - Answer text
    - Sources retrieved
    - Token usage (input and output)
    - Timestamp
    - Model used
    """
    
    def __init__(self, db_path: str = "query_logs.db"):
        """Initialize logger with database path."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT NOT NULL,
                chunks_retrieved INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                model TEXT,
                cost_estimate_usd REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_query(
        self,
        query: str,
        answer: str,
        sources: List[Dict],
        input_tokens: int,
        output_tokens: int,
        model: str = "claude-sonnet-4-20250514"
    ):
        """
        Log a query and its response.
        
        Args:
            query: User's question
            answer: Claude's response
            sources: List of source chunks used
            input_tokens: Token count for input
            output_tokens: Token count for output
            model: Model name used
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        total_tokens = input_tokens + output_tokens
        
        # Calculate approximate cost (Claude Sonnet 4 pricing as of late 2024)
        # Input: $3 per million tokens
        # Output: $15 per million tokens
        cost = (input_tokens / 1_000_000 * 3.0) + (output_tokens / 1_000_000 * 15.0)
        
        cursor.execute("""
            INSERT INTO queries (
                timestamp, query, answer, sources, chunks_retrieved,
                input_tokens, output_tokens, total_tokens, model, cost_estimate_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            query,
            answer,
            json.dumps(sources),  # Store sources as JSON
            len(sources),
            input_tokens,
            output_tokens,
            total_tokens,
            model,
            cost
        ))
        
        conn.commit()
        conn.close()
        
        print(f"[LOG] Query logged: {input_tokens} in, {output_tokens} out, ${cost:.4f}")
    
    def get_all_queries(self) -> List[Dict]:
        """Retrieve all logged queries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM queries ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        conn.close()
        
        # Convert to list of dicts
        columns = [
            'id', 'timestamp', 'query', 'answer', 'sources', 'chunks_retrieved',
            'input_tokens', 'output_tokens', 'total_tokens', 'model', 'cost_estimate_usd'
        ]
        
        results = []
        for row in rows:
            result = dict(zip(columns, row))
            result['sources'] = json.loads(result['sources'])
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get aggregate statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_queries,
                SUM(input_tokens) as total_input_tokens,
                SUM(output_tokens) as total_output_tokens,
                SUM(total_tokens) as total_tokens,
                SUM(cost_estimate_usd) as total_cost,
                AVG(input_tokens) as avg_input_tokens,
                AVG(output_tokens) as avg_output_tokens,
                AVG(chunks_retrieved) as avg_chunks
            FROM queries
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_queries': row[0] or 0,
            'total_input_tokens': row[1] or 0,
            'total_output_tokens': row[2] or 0,
            'total_tokens': row[3] or 0,
            'total_cost': row[4] or 0.0,
            'avg_input_tokens': row[5] or 0.0,
            'avg_output_tokens': row[6] or 0.0,
            'avg_chunks': row[7] or 0.0
        }
    
    def export_to_json(self, filepath: str = "query_logs.json"):
        """Export all logs to JSON file for backup/analysis."""
        queries = self.get_all_queries()
        
        with open(filepath, 'w') as f:
            json.dump(queries, f, indent=2)
        
        print(f"Exported {len(queries)} queries to {filepath}")


if __name__ == "__main__":
    # Test the logger
    logger = QueryLogger()
    
    # Show stats
    stats = logger.get_stats()
    print("\nQuery Log Statistics:")
    print("=" * 50)
    print(f"Total queries: {stats['total_queries']}")
    print(f"Total tokens: {stats['total_tokens']:,}")
    print(f"  - Input: {stats['total_input_tokens']:,}")
    print(f"  - Output: {stats['total_output_tokens']:,}")
    print(f"Total cost: ${stats['total_cost']:.4f}")
    print(f"\nAverage per query:")
    print(f"  - Input tokens: {stats['avg_input_tokens']:.0f}")
    print(f"  - Output tokens: {stats['avg_output_tokens']:.0f}")
    print(f"  - Chunks retrieved: {stats['avg_chunks']:.1f}")
    print("=" * 50)