import sqlite3
import functools
import os
import time
from datetime import datetime

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

# --- New Logging Decorator ---
def log_queries(func):
    """
    Decorator that logs the SQL query with a timestamp before executing it.
    It expects the query to be passed as a keyword argument named 'query'.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from the keyword arguments for logging.
        query_string = kwargs.get('query')
        if query_string:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"LOG [{timestamp}]: Executing query -> {query_string}")
        
        # Execute the original function and return its result.
        return func(*args, **kwargs)
    return wrapper


# --- Caching Decorator ---
query_cache = {}

def cache_query(func):
    """
    Decorator that caches the result of a function based on its 'query' keyword argument.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query_string = kwargs.get('query')
        if not query_string:
            return func(conn, *args, **kwargs)

        if query_string in query_cache:
            print(f"LOG: 🧠 Found in cache. Returning cached result for query: '{query_string}'")
            return query_cache[query_string]
        
        print(f"LOG: Executing query and caching result for: '{query_string}'")
        result = func(conn, *args, **kwargs)
        
        query_cache[query_string] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetches users from the database. Results will be cached.
    """
    time.sleep(1) 
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

@with_db_connection
@log_queries # Applying the new logging decorator
def fetch_all_users_with_logging(conn, query):
    """
    Fetches users from the database and logs the query.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# ---- DEMONSTRATION 1: QUERY CACHING ----
print("--- DEMONSTRATING QUERY CACHING ---")

print("\n1. First call (should be slow and execute the query)...")
start_time = time.time()
users = fetch_users_with_cache(query="SELECT * FROM users")
end_time = time.time()
print(f"   -> Result: {users}")
print(f"   -> Time taken: {end_time - start_time:.2f} seconds")


print("\n2. Second call (should be fast and return from cache)...")
start_time = time.time()
users_again = fetch_users_with_cache(query="SELECT * FROM users")
end_time = time.time()
print(f"   -> Result: {users_again}")
print(f"   -> Time taken: {end_time - start_time:.2f} seconds")

print("\n3. Third call with a different query (should be slow)...")
start_time = time.time()
alice = fetch_users_with_cache(query="SELECT * FROM users WHERE name = 'Alice'")
end_time = time.time()
print(f"   -> Result: {alice}")
print(f"   -> Time taken: {end_time - start_time:.2f} seconds")


# ---- DEMONSTRATION 2: QUERY LOGGING ----
print("\n\n--- DEMONSTRATING QUERY LOGGER ---")
# This call will use the new decorator to log the query with a timestamp.
all_users = fetch_all_users_with_logging(query="SELECT * FROM users")
print(f"   -> Result: {all_users}")


# Clean up the created database file
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

