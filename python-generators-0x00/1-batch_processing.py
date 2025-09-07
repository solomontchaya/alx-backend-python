#!/usr/bin/python3
"""
A script to fetch users in batches from a database and process them.
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

def stream_users_in_batches(batch_size=5):
    """
    Connects to the database and yields rows from the user_data table
    in batches of the specified size.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data;")

        # Loop 1: Continuously fetch batches until the data is exhausted.
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                # No more rows to fetch
                break
            yield batch

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def batch_processing(batch_size=5):
    """
    Processes batches of users to filter those over the age of 25.
    """
    print(f"--- Processing users in batches of {batch_size} ---")
    user_generator = stream_users_in_batches(batch_size)

    # Loop 2: Iterate through each batch provided by the generator.
    for batch in user_generator:
        older_users = []
        # Loop 3: Iterate through each user within the current batch.
        for user in batch:
            # Assuming age is the 4th column (index 3)
            age = user[3]
            if age > 25:
                older_users.append(user)
        
        if older_users:
            print(f"Found {len(older_users)} users over 25 in this batch:")
            for user in older_users:
                print(f"  - {user}")
        else:
            print("No users over 25 in this batch.")

# --- Main execution block ---
if __name__ == "__main__":
    # Define the batch size
    BATCH_SIZE = 5
    # Run the batch processing
    batch_processing(BATCH_SIZE)