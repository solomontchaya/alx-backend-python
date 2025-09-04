import seed

def stream_user_ages():
    """Generator that yields user ages one by one."""
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data;")
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row['age']
    cursor.close()
    connection.close()


def average_age():
    """Compute average age without loading all data into memory."""
    total = 0
    count = 0
    for age in stream_user_ages():  # loop 1
        total += age
        count += 1
    if count == 0:
        avg = 0
    else:
        avg = total / count
    print(f"Average age of users: {avg}")
