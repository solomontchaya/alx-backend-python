from seed import connect_to_prodev, stream_rows

connection = connect_to_prodev()

for row in stream_rows(connection):
    print(row)
