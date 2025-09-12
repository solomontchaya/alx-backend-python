import sqlite3
import functools
import os

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


def log_queries(func):
    """
    A decorator that logs the SQL query passed to the decorated function
    before executing it.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Identify the query from the function's arguments.
        # It could be a positional argument (in `args`) or a keyword argument (in `kwargs`).
        query = kwargs.get('query') or (args[0] if args else None)

        # 2. Log the query to the console.
        if query:
            print(f"📄 LOG: Executing query -> \"{query}\"")
        else:
            print("📄 LOG: No query found to log.")

        # 3. Execute the original function (e.g., fetch_all_users) and get its result.
        result = func(*args, **kwargs)

        # 4. Return the result of the original function.
        return result
    return wrapper


@log_queries
def fetch_all_users(query):
    """Fetches all users from the database using a given query."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# ---- Let's run it and see the output ----
print("Fetching all users...")
users = fetch_all_users(query="SELECT * FROM users")
print("\n✅ Query Result:")
print(users)

print("\n-------------------\n")

print("Fetching a single user by name...")
user_bob = fetch_all_users("SELECT * FROM users WHERE name = 'Bob'")
print("\n✅ Query Result:")
print(user_bob)

# Clean up the created database file
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)