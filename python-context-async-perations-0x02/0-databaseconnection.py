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

# --- New Class-Based Context Manager ---
class DatabaseConnection:
    """
    A class-based context manager for handling SQLite database connections.
    """
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """
        Opens the database connection when entering the 'with' block.
        """
        print("LOG: [CM] 🔌 Opening database connection.")
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection when exiting the 'with' block.
        The additional arguments handle exceptions if they occur inside the block.
        """
        if self.conn:
            self.conn.close()
            print("LOG: [CM] 🔌 Closing database connection.")


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
            result = func(conn, *args, **kwargs)
            return result
        finally:
            if conn:
                conn.close()
    return wrapper

def log_queries(func):
    """
    Decorator that logs the SQL query with a timestamp before executing it.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query_string = kwargs.get('query')
        if query_string:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"LOG [{timestamp}]: Executing query -> {query_string}")
        return func(*args, **kwargs)
    return wrapper

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
    time.sleep(1) 
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

@with_db_connection
@log_queries
def fetch_all_users_with_logging(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# ---- DEMONSTRATION 1: QUERY CACHING ----
print("--- DEMONSTRATING QUERY CACHING ---")
# ... (previous demonstrations remain unchanged) ...
print("\n1. First call...")
users = fetch_users_with_cache(query="SELECT * FROM users")
print("\n2. Second call...")
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print("\n3. Third call...")
alice = fetch_users_with_cache(query="SELECT * FROM users WHERE name = 'Alice'")


# ---- DEMONSTRATION 2: QUERY LOGGING ----
print("\n\n--- DEMONSTRATING QUERY LOGGER ---")
all_users = fetch_all_users_with_logging(query="SELECT * FROM users")


# ---- DEMONSTRATION 3: CLASS-BASED CONTEXT MANAGER ----
print("\n\n--- DEMONSTRATING CONTEXT MANAGER ---")
try:
    # The 'with' statement automatically calls __enter__ at the start
    # and __exit__ at the end.
    with DatabaseConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print(f"   -> Query Results: {results}")
except Exception as e:
    print(f"An error occurred: {e}")


# Clean up the created database file
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

