from itertools import islice
stream_obj = __import__('0-stream_users')

# iterate over the generator function and print only the first 6 rows

for user in islice(stream_obj.stream_users(), 6):
    print(user)