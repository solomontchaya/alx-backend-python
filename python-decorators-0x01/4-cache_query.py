import sqlite3
import functools
import os
import time

# --- Setup: Create a dummy database for the example to run ---
DB_FILE = 'users.db'
if os.path.exists(DB_FILE):
    os.remove(DB_FILE) # Start with a fresh database each time

conn_setup = sqlite3.connect(DB_FILE)
cursor_setup = conn_setup.cursor()
cursor_setup.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
''')
cursor_setup.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@web.com')")
cursor_setup.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@web.com')")
conn_setup.commit()
conn_setup.close()
# --- End Setup ---


def with_db_connection(func):
    """
    Decorator that opens a database connection, passes it to the function as the
    first argument, and ensures the connection is closed afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            # We remove the print statements from this decorator to reduce noise
            # for the caching example.
            result = func(conn, *args, **kwargs)
            return result
        finally:
            if conn:
                conn.close()
    return wrapper

# --- New Caching Decorator ---

# A simple dictionary to act as our in-memory cache.
query_cache = {}

def cache_query(func):
    """
    Decorator that caches the result of a function based on its 'query' keyword argument.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # The query string is used as the key for our cache.
        query_string = kwargs.get('query')
        if not query_string:
            # If no query string is provided, we can't cache, so just run the function.
            return func(conn, *args, **kwargs)

        # 1. Check if the result for this query is already in the cache.
        if query_string in query_cache:
            print(f"LOG: 🧠 Found in cache. Returning cached result for query: '{query_string}'")
            return query_cache[query_string]
        
        # 2. If not in cache, execute the function to get the result.
        print(f"LOG: Executing query and caching result for: '{query_string}'")
        result = func(conn, *args, **kwargs)
        
        # 3. Store the new result in the cache.
        query_cache[query_string] = result
        return result
    return wrapper


@with_db_connection
@cache_query # The cache decorator is applied, it will run inside the connection.
def fetch_users_with_cache(conn, query):
    """
    Fetches users from the database. Results will be cached.
    """
    # Simulate a delay to represent a slow database query.
    time.sleep(1) 
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# ---- Let's run it and see the output ----
print("--- DEMONSTRATING QUERY CACHING ---")

# First call: This will be slow, execute the query, and cache the result.
print("\n1. First call (should be slow and execute the query)...")
start_time = time.time()
users = fetch_users_with_cache(query="SELECT * FROM users")
end_time = time.time()
print(f"   -> Result: {users}")
print(f"   -> Time taken: {end_time - start_time:.2f} seconds")


# Second call: This should be very fast as it will hit the cache.
print("\n2. Second call (should be fast and return from cache)...")
start_time = time.time()
users_again = fetch_users_with_cache(query="SELECT * FROM users")
end_time = time.time()
print(f"   -> Result: {users_again}")
print(f"   -> Time taken: {end_time - start_time:.2f} seconds")

# Third call with a different query: This will be slow again as it's a new query.
print("\n3. Third call with a different query (should be slow)...")
start_time = time.time()
alice = fetch_users_with_cache(query="SELECT * FROM users WHERE name = 'Alice'")
end_time = time.time()
print(f"   -> Result: {alice}")
print(f"   -> Time taken: {end_time - start_time:.2f} seconds")


# Clean up the created database file
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

