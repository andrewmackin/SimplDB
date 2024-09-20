# test_dbms.py

import unittest
import shutil
from dbms import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.data_dir = 'test_data'
        shutil.rmtree(self.data_dir, ignore_errors=True)
        self.db = Database(data_dir=self.data_dir)

    def test_create_table(self):
        result = self.db.execute("CREATE TABLE users (id, name)")
        self.assertEqual(result, "Table users created.")

    def test_insert_into(self):
        self.db.execute("CREATE TABLE users (id, name)")
        result = self.db.execute("INSERT INTO users VALUES (1, 'Alice')")
        self.assertEqual(result, "1 row inserted into users.")

    def test_select_from(self):
        self.db.execute("CREATE TABLE users (id, name)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice')")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob')")
        result = self.db.execute("SELECT * FROM users")
        expected = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
        self.assertEqual(result, expected)

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
