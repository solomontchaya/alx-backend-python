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
            print("LOG: 🔌 Database connection opened.")
            result = func(conn, *args, **kwargs)
            return result
        finally:
            if conn:
                conn.close()
                print("LOG: 🔌 Database connection closed.")
    return wrapper


def retry_on_failure(retries=3, delay=1):
    """
    A decorator factory that retries a function if it raises an exception.
    :param retries: The maximum number of times to retry the function.
    :param delay: The number of seconds to wait between retries.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    # Attempt to execute the wrapped function.
                    return func(*args, **kwargs)
                except Exception as e:
                    # If an exception occurs, check if this is the last retry.
                    if i < retries - 1:
                        print(f"LOG: ⚠️ Operation failed with error: {e}. Retrying in {delay}s... (Attempt {i+1}/{retries})")
                        time.sleep(delay)
                    else:
                        # If it's the last retry, log and re-raise the exception.
                        print(f"LOG: ❌ Operation failed after {retries} retries.")
                        raise e
        return wrapper
    return decorator


# A simple counter to simulate transient failures for the demonstration.
call_counter = 0

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetches users, but is designed to fail the first 2 times to test the retry decorator.
    """
    global call_counter
    call_counter += 1

    if call_counter <= 2:
        print(f"LOG: Simulating a failure on attempt number {call_counter}...")
        # Simulate a common transient error.
        raise sqlite3.OperationalError("Database is locked, please try again.")
    else:
        print(f"LOG: ✅ Operation successful on attempt number {call_counter}.")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()


# ---- Let's run it and see the output ----
print("--- DEMONSTRATING RETRY ON FAILURE ---")
try:
    # Attempt to fetch users with automatic retry on failure.
    users = fetch_users_with_retry()
    print("\n✅ Successfully fetched users:")
    print(users)
except Exception as e:
    print(f"\n❌ Could not fetch users after multiple retries. Final error: {e}")


# Clean up the created database file
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
