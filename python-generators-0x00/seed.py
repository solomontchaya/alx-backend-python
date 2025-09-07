print("--- Script is starting up ---")
import mysql.connector
from mysql.connector import errorcode
import csv
import os

# --- IMPORTANT: UPDATE YOUR DATABASE CREDENTIALS HERE ---
DB_CONFIG = {
    'user': 'root',      # Replace with your MySQL username
    'password': 'Theloveofchrist@1',  # Replace with your MySQL password
    'host': 'localhost'           # Replace if your DB is not on localhost
}
DB_NAME = 'alx_travel_db'  # Database name

def connect_db():
    """Connects to the MySQL database server."""
    try:
        print("Connecting to MySQL server...")
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connection to MySQL server successful!")
        return connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Something is wrong with your user name or password")
        else:
            print(f"❌ Error connecting to MySQL: {err}")
        return None

def create_database(connection):
    """Creates the database ALX_prodev if it does not exist."""
    if not connection:
        return
    
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database '{DB_NAME}' checked/created successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Failed to create database: {err}")
    finally:
        cursor.close()

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL."""
    try:
        # Update config to connect directly to the specific database
        config = DB_CONFIG.copy()
        config['database'] = DB_NAME
        
        print(f"Connecting to database '{DB_NAME}'...")
        connection = mysql.connector.connect(**config)
        print(f"✅ Connection to '{DB_NAME}' successful!")
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Error connecting to database '{DB_NAME}': {err}")
        return None

def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields."""
    if not connection:
        return
        
    cursor = connection.cursor()
    # SQL command to create the table
    # user_id is VARCHAR(36) to accommodate UUID format.
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(3, 0) NOT NULL,
        INDEX(user_id)
    )
    """
    try:
        cursor.execute(create_table_query)
        print("Table 'user_data' checked/created successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Failed creating table: {err}")
    finally:
        cursor.close()

def insert_data(connection, data):
    """Inserts data into the database if it does not exist."""
    if not connection:
        return
        
    cursor = connection.cursor()
    
    # Using INSERT IGNORE to prevent errors if a user_id (Primary Key) already exists.
    insert_query = """
    INSERT IGNORE INTO user_data (user_id, name, email, age) 
    VALUES (%s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(insert_query, data)
        connection.commit() # Commit the changes to the database
        print(f"✅ Successfully inserted {cursor.rowcount} new rows of data.")
    except mysql.connector.Error as err:
        print(f"❌ Error inserting data: {err}")
        connection.rollback() # Rollback in case of error
    finally:
        cursor.close()

def main():
    """Main function to orchestrate the database setup and seeding."""
    
    # Step 1: Connect to the MySQL server
    server_connection = connect_db()
    
    # Step 2: Create the database
    if server_connection:
        create_database(server_connection)
        server_connection.close()
        print("Server connection closed.")

    # Step 3: Connect to the specific ALX_prodev database
    db_connection = connect_to_prodev()
    
    if db_connection:
        # Step 4: Create the user_data table
        create_table(db_connection)
        
        # Step 5: Read data from CSV and insert into the table
        csv_file_path = 'user_data.csv'
        if not os.path.exists(csv_file_path):
            print(f"❌ Error: The file '{csv_file_path}' was not found.")
            print("Please create it in the same directory as the script.")
        else:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader) # Skip the header row
                
                data_to_insert = [tuple(row) for row in reader]
                
                if data_to_insert:
                    insert_data(db_connection, data_to_insert)
                else:
                    print("CSV file is empty. No data to insert.")

        # Close the final connection
        db_connection.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()