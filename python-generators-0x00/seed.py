import mysql.connector
import csv
import uuid

# --------------------------
# Connect to MySQL server
# --------------------------
def connect_db():
    """Connect to MySQL server (no specific database)."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""  # replace with your MySQL password
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# --------------------------
# Create database ALX_prodev
# --------------------------
def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
    cursor.close()
    print("Database created successfully")

# --------------------------
# Connect to ALX_prodev database
# --------------------------
def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # replace with your MySQL password
            database="alx_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# --------------------------
# Create table user_data
# --------------------------
def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL
        );
    """)
    cursor.close()
    print("Table user_data created successfully")

# --------------------------
# Insert CSV data
# --------------------------
def insert_data(connection, filename):
    cursor = connection.cursor()
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user_id = row.get('user_id') or str(uuid.uuid4())
            name = row['name']
            email = row['email']
            age = row['age']
            # Insert only if user_id does not exist
            cursor.execute("""
                INSERT IGNORE INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s);
            """, (user_id, name, email, age))
    connection.commit()
    cursor.close()
    print("Data inserted successfully")

# --------------------------
# Generator function
# --------------------------
def stream_rows(connection):
    """Yield rows one by one from user_data."""
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data;")
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row
    cursor.close()
