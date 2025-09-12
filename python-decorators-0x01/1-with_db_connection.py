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


def with_db_connection(func):
    """
    Decorator that opens a database connection, passes it to the function as the
    first argument, and ensures the connection is closed afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None  # Initialize conn to None
        try:
            # 1. Open the database connection.
            conn = sqlite3.connect(DB_FILE)
            print("LOG: 🔌 Database connection opened.")
            # 2. Call the original function, passing the connection object
            #    as the first positional argument.
            result = func(conn, *args, **kwargs)
            # 3. Return the result from the original function.
            return result
        finally:
            # 4. Ensure the connection is closed, even if errors occurred.
            if conn:
                conn.close()
                print("LOG: 🔌 Database connection closed.")
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetches a single user from the database by their ID.
    Expects a database connection `conn` to be passed by a decorator.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# ---- Let's run it and see the output ----
print("Fetching user with ID 1...")
# Note: We don't pass the 'conn' object ourselves; the decorator handles it!
user = get_user_by_id(user_id=1)

print("\n✅ Query Result:")
print(user)


# Clean up the created database file
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

