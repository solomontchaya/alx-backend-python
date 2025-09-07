#!/usr/bin/python3
"""
A script to calculate the average age of users in a memory-efficient way.
"""
import mysql.connector
from decimal import Decimal

# --- Database Configuration ---
# Update these with your MySQL server details
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'ALX_prodev'
}

def stream_user_ages():
    """
    Connects to the database and yields each user's age one by one.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # We only need the age, so we select just that column.
        cursor.execute("SELECT age FROM user_data;")
        
        # Loop 1: Iterates over the cursor to fetch each row.
        for row in cursor:
            yield row[0] # Yield the age, which is the first item in the row tuple.
            
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# --- Main execution block to calculate the average ---
if __name__ == "__main__":
    total_age = Decimal(0)
    user_count = 0
    
    # Create the generator object
    age_generator = stream_user_ages()
    
    # Loop 2: Iterates through the ages provided by the generator.
    for age in age_generator:
        total_age += age
        user_count += 1
        
    # Calculate the average, handling the case of an empty table.
    if user_count > 0:
        average_age = total_age / user_count
        print(f"Average age of users: {average_age:.2f}")
    else:
        print("No users found to calculate an average age.")