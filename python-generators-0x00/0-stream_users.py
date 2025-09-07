#!/usr/bin/python3
"""
A script that contains a generator function to stream users from a database.
"""
import mysql.connector

# --- Database Configuration ---
# Update these with your MySQL server details
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'ALX_prodev'
}

def stream_users():
    """
    Connects to the database and streams rows from the user_data table one by one.
    This function uses a generator.
    """
    connection = None
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute the query to select all users
        cursor.execute("SELECT * FROM user_data;")

        # This single loop iterates over the cursor, which fetches rows from the server.
        # The 'yield' keyword turns this function into a generator.
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Ensure the connection is always closed
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# --- Main execution block to demonstrate the generator ---
if __name__ == "__main__":
    print("Streaming users from the database:")
    
    # Create the generator object by calling the function
    user_generator = stream_users()

    # Iterate through the generator to get each user one by one
    for user in user_generator:
        print(user)