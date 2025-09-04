import seed

def stream_users_in_batches(batch_size):
    """Generator that yields users in batches."""
    offset = 0
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    
    while True:
        cursor.execute(f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}")
        rows = cursor.fetchall()
        if not rows:
            break
        yield rows
        offset += batch_size

    cursor.close()
    connection.close()


def batch_processing(batch_size):
    """Process batches to filter users over age 25."""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
                return user
