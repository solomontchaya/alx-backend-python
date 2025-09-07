#!/usr/bin/python3
"""
A script to fetch users in batches, filter them, and return a final list.
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
    in batches of the specified size. This function is unchanged.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data;")

        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def batch_processing_with_return(batch_size=5):
    """
    Processes batches of users to filter those over 25 and returns
    a single list containing all the results.
    """
    print(f"--- Processing all users... ---")
    user_generator = stream_users_in_batches(batch_size)
    all_older_users = []

    # Loop through each batch from the generator
    for batch in user_generator:
        # Loop through each user within the batch
        for user in batch:
            # Assuming age is the 4th column (index 3)
            age = user[3]
            if age > 25:
                all_older_users.append(user)
    
    # The 'return' statement sends the final list back to the caller
    return all_older_users

# --- Main execution block ---
if __name__ == "__main__":
    BATCH_SIZE = 5
    
    # Call the function and store the returned list in a variable
    filtered_users = batch_processing_with_return(BATCH_SIZE)
    
    # Now, you can work with the complete list of filtered users
    print(f"\n--- Final Result: Found {len(filtered_users)} users over 25 ---")
    for user in filtered_users:
        print(user)