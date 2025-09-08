import time
import sqlite3
import functools

query_cache = {}

def with_db_connection(func):
    """Decorator to automatically handle DB connection"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper


def cache_query(func):
    """Decorator to cache query results based on SQL query string"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Determine the query string
        query = None
        if args:
            query = args[0]  # first positional arg after conn
        elif "query" in kwargs:
            query = kwargs["query"]

        if query in query_cache:
            print(f"[CACHE] Returning cached result for query: {query}")
            return query_cache[query]

        # Otherwise execute and store result
        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        print(f"[CACHE] Stored result for query: {query}")
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# ==== Example usage ====
if __name__ == "__main__":
    # First call → hits DB and caches
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(users)

    # Second call → uses cache
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(users_again)
