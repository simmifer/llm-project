"""
Query Log Viewer

View and analyze logged queries, responses, and token usage.
Run with: python view_logs.py
"""

from query_logger import QueryLogger
import json
from datetime import datetime


def display_stats():
    """Display aggregate statistics."""
    logger = QueryLogger()
    stats = logger.get_stats()
    
    print("\n" + "=" * 70)
    print("QUERY LOG STATISTICS")
    print("=" * 70)
    print(f"Total queries: {stats['total_queries']}")
    print(f"\nToken Usage:")
    print(f"  Total tokens: {stats['total_tokens']:,}")
    print(f"  Input tokens: {stats['total_input_tokens']:,}")
    print(f"  Output tokens: {stats['total_output_tokens']:,}")
    print(f"\nCost Analysis:")
    print(f"  Total cost: ${stats['total_cost']:.4f}")
    print(f"  Average cost per query: ${stats['total_cost'] / max(stats['total_queries'], 1):.4f}")
    print(f"\nAverages per query:")
    print(f"  Input tokens: {stats['avg_input_tokens']:.0f}")
    print(f"  Output tokens: {stats['avg_output_tokens']:.0f}")
    print(f"  Chunks retrieved: {stats['avg_chunks']:.1f}")
    print("=" * 70 + "\n")


def display_recent_queries(n: int = 10):
    """Display the N most recent queries."""
    logger = QueryLogger()
    queries = logger.get_all_queries()[:n]
    
    print(f"\nMOST RECENT {min(n, len(queries))} QUERIES")
    print("=" * 70)
    
    for i, q in enumerate(queries, 1):
        # Parse timestamp
        ts = datetime.fromisoformat(q['timestamp'])
        
        print(f"\n[{i}] {ts.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Query: {q['query'][:100]}{'...' if len(q['query']) > 100 else ''}")
        print(f"Tokens: {q['input_tokens']} in, {q['output_tokens']} out (${q['cost_estimate_usd']:.4f})")
        print(f"Chunks: {q['chunks_retrieved']}")
        print("-" * 70)


def display_query_details(query_id: int):
    """Display full details of a specific query."""
    logger = QueryLogger()
    queries = logger.get_all_queries()
    
    # Find query by ID
    query = None
    for q in queries:
        if q['id'] == query_id:
            query = q
            break
    
    if not query:
        print(f"Query ID {query_id} not found.")
        return
    
    ts = datetime.fromisoformat(query['timestamp'])
    
    print("\n" + "=" * 70)
    print(f"QUERY DETAILS - ID {query_id}")
    print("=" * 70)
    print(f"Timestamp: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {query['model']}")
    print(f"\nQuery:")
    print(query['query'])
    print(f"\nAnswer:")
    print(query['answer'])
    print(f"\nToken Usage:")
    print(f"  Input: {query['input_tokens']}")
    print(f"  Output: {query['output_tokens']}")
    print(f"  Total: {query['total_tokens']}")
    print(f"  Cost: ${query['cost_estimate_usd']:.4f}")
    print(f"\nSources Retrieved ({query['chunks_retrieved']} chunks):")
    for i, source in enumerate(query['sources'], 1):
        print(f"  {i}. {source['source']} (similarity: {source['similarity']:.3f})")
    print("=" * 70 + "\n")


def export_logs():
    """Export all logs to JSON."""
    logger = QueryLogger()
    logger.export_to_json()
    print("Logs exported to query_logs.json")


def interactive_menu():
    """Interactive menu for viewing logs."""
    while True:
        print("\n" + "=" * 70)
        print("QUERY LOG VIEWER")
        print("=" * 70)
        print("1. View statistics")
        print("2. View recent queries")
        print("3. View query details")
        print("4. Export logs to JSON")
        print("5. Exit")
        print("=" * 70)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            display_stats()
        elif choice == "2":
            n = input("How many recent queries to show? (default 10): ").strip()
            n = int(n) if n.isdigit() else 10
            display_recent_queries(n)
        elif choice == "3":
            query_id = input("Enter query ID: ").strip()
            if query_id.isdigit():
                display_query_details(int(query_id))
            else:
                print("Invalid query ID")
        elif choice == "4":
            export_logs()
        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("Invalid option. Please select 1-5.")


if __name__ == "__main__":
    import sys
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "stats":
            display_stats()
        elif command == "recent":
            n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            display_recent_queries(n)
        elif command == "export":
            export_logs()
        elif command == "details" and len(sys.argv) > 2:
            display_query_details(int(sys.argv[2]))
        else:
            print("Usage:")
            print("  python view_logs.py stats          - Show statistics")
            print("  python view_logs.py recent [N]     - Show N recent queries")
            print("  python view_logs.py details <ID>   - Show query details")
            print("  python view_logs.py export         - Export to JSON")
            print("  python view_logs.py                - Interactive menu")
    else:
        # No arguments, show interactive menu
        interactive_menu()