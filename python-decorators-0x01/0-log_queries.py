import sqlite3
import functools

# ===== Decorator to log SQL queries =====
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get query argument (either positional or keyword)
        query = None
        if args:
            query = args[0]
        elif "query" in kwargs:
            query = kwargs["query"]

        if query:
            print(f"[LOG] Executing SQL Query: {query}")

        return func(*args, **kwargs)
    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# ===== Example usage =====
if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)