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


def transactional(func):
    """
    Decorator that wraps a function in a database transaction.
    It commits the transaction if the function executes successfully and
    rolls it back if any exception occurs.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # The wrapped function (e.g., update_user_email) is called here.
            result = func(conn, *args, **kwargs)
            # If the function completes without any errors, commit the changes.
            conn.commit()
            print("LOG: ✅ Transaction committed successfully.")
            return result
        except Exception as e:
            # If any error occurs during the function's execution, roll back all changes.
            print(f"LOG: ❌ An error occurred. Rolling back transaction. Error: {e}")
            conn.rollback()
            # Re-raise the exception to notify the caller that something went wrong.
            raise
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetches a single user from the database by their ID.
    (Used here for verification purposes).
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


@with_db_connection
@transactional # Applied second, so it runs inside with_db_connection
def update_user_email(conn, user_id, new_email):
    """Updates a user's email. This operation will be committed."""
    print(f"\nAttempting to update user {user_id}'s email to {new_email}...")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    print("...Update executed.")


@with_db_connection
@transactional
def add_user_with_error(conn, name, email):
    """Attempts to add a user, but is designed to fail to show rollback."""
    print(f"\nAttempting to add user '{name}' with existing email '{email}'...")
    cursor = conn.cursor()
    # This will fail because the email 'alice@web.com' is marked as UNIQUE and already exists.
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))


# ---- Let's run it and see the output ----

# 1. Successful Transaction (COMMIT)
print("--- DEMONSTRATING A SUCCESSFUL COMMIT ---")
print("User 1 before update:", get_user_by_id(user_id=1))
update_user_email(user_id=1, new_email='alice.new@web.com')
print("User 1 after update:", get_user_by_id(user_id=1))


# 2. Failed Transaction (ROLLBACK)
print("\n\n--- DEMONSTRATING A FAILED ROLLBACK ---")
print("User 1 before failed operation:", get_user_by_id(user_id=1))
try:
    # We call a function that will cause a database error.
    add_user_with_error(name="Eve", email="alice@web.com")
except sqlite3.IntegrityError:
    # The decorator will log the rollback, and we catch the expected error.
    print("...Caught expected database error.")

print("User 1 after failed operation (email should be unchanged):", get_user_by_id(user_id=1))


# Clean up the created database file
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

