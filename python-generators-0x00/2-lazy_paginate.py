#!/usr/bin/python3
"""
A script to lazily paginate through users from a database.
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

def paginate_users(page_size, offset):
    """
    Fetches a single page of users from the database.
    This is a regular function, not a generator.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s;"
        cursor.execute(query, (page_size, offset))
        
        page = cursor.fetchall()
        return page
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def lazy_paginate(page_size):
    """
    A generator that lazily fetches pages of users by calling paginate_users.
    It only fetches the next page when it is requested.
    """
    offset = 0
    # This single loop continues as long as there are pages to fetch.
    while True:
        # Fetch the next page of data
        page = paginate_users(page_size=page_size, offset=offset)
        
        # If the page is empty, there's no more data to fetch
        if not page:
            break
            
        # Yield the current page and pause until the next one is requested
        yield page
        
        # Prepare the offset for the next page request
        offset += page_size

# --- Main execution block to demonstrate lazy pagination ---
if __name__ == "__main__":
    PAGE_SIZE = 5
    page_generator = lazy_paginate(page_size=PAGE_SIZE)
    
    page_number = 1
    for page in page_generator:
        print(f"--- Page {page_number} ---")
        for user in page:
            print(user)
        
        # To make the lazy loading obvious, we wait for user input
        input("Press Enter to fetch the next page...")
        page_number += 1
        
    print("--- No more pages ---")