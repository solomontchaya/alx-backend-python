# Python Generators Project

This project demonstrates the use of Python generators for efficient data processing with SQL databases. It includes tasks for database setup, streaming data, batch processing, pagination, and memory-efficient aggregation.

## Tasks

### 0. Getting Started with Python Generators
**Objective**: Set up a MySQL database and populate it with sample data.

**Files**:
- `seed.py`
- `README.md`

**Instructions**:
- Create a MySQL database named `ALX_prodev`
- Create a table `user_data` with fields:
  - `user_id` (Primary Key, UUID, Indexed)
  - `name` (VARCHAR, NOT NULL)
  - `email` (VARCHAR, NOT NULL)
  - `age` (DECIMAL, NOT NULL)
- Populate the database with data from `user_data.csv`

**Prototypes in `seed.py`**:
- `def connect_db()`: Connects to the MySQL database server
- `def create_database(connection)`: Creates the database `ALX_prodev` if it doesn't exist
- `def connect_to_prodev()`: Connects to the `ALX_prodev` database in MySQL
- `def create_table(connection)`: Creates the `user_data` table if it doesn't exist
- `def insert_data(connection, data)`: Inserts data from CSV file into the database

### 1. Generator That Streams Rows from an SQL Database
**Objective**: Create a generator that streams rows from the SQL database one by one.

**File**: `0-stream_users.py`

**Instructions**:
- Implement a function `stream_users()` that uses a generator to fetch rows one by one from the `user_data` table
- Use the `yield` keyword to create the generator
- The function should have no more than 1 loop

**Prototype**:
```python
def stream_users():
    # Implementation
```

### 2. Batch Processing Large Data
**Objective**: Create a generator to fetch and process data in batches from the database.

**File**: `1-batch_processing.py`

**Instructions**:
- Implement `stream_users_in_batches(batch_size)` to fetch rows in batches
- Implement `batch_processing(batch_size)` to process each batch and filter users over age 25
- Use no more than 3 loops in your code
- Use the `yield` generator

**Prototypes**:
```python
def stream_users_in_batches(batch_size):
    # Implementation

def batch_processing(batch_size):
    # Implementation
```

### 3. Lazy Loading Paginated Data
**Objective**: Simulate fetching paginated data from the database using a generator to lazily load each page.

**File**: `2-lazy_paginate.py`

**Instructions**:
- Implement a generator function `lazy_paginate(page_size)` that uses `paginate_users(page_size, offset)` to fetch pages
- Only fetch the next page when needed
- Use only one loop
- Include the `paginate_users` function in your code
- Use the `yield` generator

**Prototype**:
```python
def lazy_paginate(page_size):
    # Implementation
```

### 4. Memory-Efficient Aggregation with Generators
**Objective**: Use a generator to compute a memory-efficient aggregate function (average age).

**File**: `4-stream_ages.py`

**Instructions**:
- Implement a generator `stream_user_ages()` that yields user ages one by one
- Use the generator to calculate the average age without loading the entire dataset into memory
- Print "Average age of users: average_age"
- Use no more than two loops
- Do not use SQL AVERAGE function

**Prototype**:
```python
def stream_user_ages():
    # Implementation

# Calculate and print average age
```

## Setup and Usage

1. Install required dependencies:
```bash
pip install mysql-connector-python
```

2. Set up MySQL database and credentials

3. Run the tasks:
```bash
# Task 0
python3 0-main.py

# Task 1
python3 1-main.py

# Task 2
python3 2-main.py

# Task 3
python3 3-main.py

# Task 4
python3 4-stream_ages.py
```

## Repository Structure
```
alx-backend-python/
└── python-generators-0x00/
    ├── seed.py
    ├── 0-stream_users.py
    ├── 1-batch_processing.py
    ├── 2-lazy_paginate.py
    ├── 4-stream_ages.py
    ├── user_data.csv
    └── README.md
```