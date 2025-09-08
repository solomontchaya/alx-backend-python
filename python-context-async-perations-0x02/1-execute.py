import sqlite3

class ExecuteQuery:
    """Custom context manager to execute queries with parameters"""

    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else ()
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
        return False  # propagate exceptions if any

# ==== Example usage ====
if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    with ExecuteQuery("users.db", query, (25,)) as results:
        print(results)