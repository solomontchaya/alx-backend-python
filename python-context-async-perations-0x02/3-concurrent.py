import sqlite3
import functools
import os
import time
from datetime import datetime
# Note: The new section requires 'aiosqlite'. Install with: pip install aiosqlite
import asyncio
import aiosqlite


# --- Setup: Create a dummy database for the example to run ---
DB_FILE = 'users.db'
if os.path.exists(DB_FILE):
    os.remove(DB_FILE) # Start with a fresh database each time

conn_setup = sqlite3.connect(DB_FILE)
cursor_setup = conn_setup.cursor()
# Updated schema to include age
cursor_setup.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER
    )
''')
# Updated data to include more examples
cursor_setup.execute("INSERT INTO users (name, email, age) VALUES ('Alice', 'alice@web.com', 30)")
cursor_setup.execute("INSERT INTO users (name, email, age) VALUES ('Bob', 'bob@web.com', 22)")
cursor_setup.execute("INSERT INTO users (name, email, age) VALUES ('Charlie', 'charlie@web.com', 45)")
cursor_setup.execute("INSERT INTO users (name, email, age) VALUES ('Diana', 'diana@web.com', 50)")
conn_setup.commit()
conn_setup.close()
# --- End Setup ---


# --- Context Manager for Connection only ---
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
        """
        if self.conn:
            self.conn.close()
            print("LOG: [CM] 🔌 Closing database connection.")

# --- Reusable Context Manager for Executing Queries ---
class ExecuteQuery:
    """
    A reusable context manager to connect, execute a query, and close the connection.
    """
    def __init__(self, db_name, query, params=()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None

    def __enter__(self):
        """
        Opens connection, executes the query, and returns the results.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            cursor = self.conn.cursor()
            cursor.execute(self.query, self.params)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error during query execution: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures the database connection is closed.
        """
        if self.conn:
            self.conn.close()


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
        cache_key = (query_string, tuple(sorted(kwargs.items())))

        if not query_string:
            return func(conn, *args, **kwargs)

        if cache_key in query_cache:
            print(f"LOG: 🧠 Found in cache. Returning cached result for query: '{query_string}'")
            return query_cache[cache_key]
        
        print(f"LOG: Executing query and caching result for: '{query_string}'")
        result = func(conn, *args, **kwargs)
        query_cache[cache_key] = result
        return result
    return wrapper

# --- Asynchronous Functions ---
async def async_fetch_users():
    """Asynchronously fetches all users."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

async def async_fetch_older_users():
    """Asynchronously fetches users older than 40."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            return await cursor.fetchall()

async def fetch_concurrently():
    """Gathers and runs multiple async queries concurrently."""
    print("\n\n--- DEMONSTRATING ASYNCIO CONCURRENT QUERIES ---")
    
    # Use asyncio.gather to schedule both functions to run concurrently
    all_users_task = async_fetch_users()
    older_users_task = async_fetch_older_users()
    
    # Await the results from both tasks
    results = await asyncio.gather(all_users_task, older_users_task)
    
    all_users_result, older_users_result = results

    print(f"   -> Fetched all users (concurrently): {all_users_result}")
    print(f"   -> Fetched users older than 40 (concurrently): {older_users_result}")

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
print("\n1. First call...")
users = fetch_users_with_cache(query="SELECT * FROM users")
print("\n2. Second call...")
users_again = fetch_users_with_cache(query="SELECT * FROM users")


# ---- DEMONSTRATION 2: QUERY LOGGING ----
print("\n\n--- DEMONSTRATING QUERY LOGGER ---")
all_users = fetch_all_users_with_logging(query="SELECT * FROM users")


# ---- DEMONSTRATION 3: CLASS-BASED CONTEXT MANAGER (Connection only)----
print("\n\n--- DEMONSTRATING CONNECTION CONTEXT MANAGER ---")
with DatabaseConnection(DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print(f"   -> Query Results: {results}")


# ---- DEMONSTRATION 4: REUSABLE QUERY CONTEXT MANAGER ----
print("\n\n--- DEMONSTRATING REUSABLE QUERY CONTEXT MANAGER ---")
query_string = "SELECT * FROM users WHERE age > ?"
params = (25,)
with ExecuteQuery(DB_FILE, query_string, params) as results:
    print(f"Query: '{query_string}' with params {params}")
    print(f"   -> Query Results: {results}")

# ---- DEMONSTRATION 5: ASYNCIO CONCURRENT EXECUTION ----
# Run the main asynchronous function
asyncio.run(fetch_concurrently())


# Clean up the created database file
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

