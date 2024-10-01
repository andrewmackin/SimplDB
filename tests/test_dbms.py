import os
import unittest
import shutil
from dbms import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.data_dir = 'test_data'
        shutil.rmtree(self.data_dir, ignore_errors=True)
        os.makedirs(self.data_dir, exist_ok=True)
        self.db = Database(data_dir=self.data_dir)

    def test_create_table(self):
        result = self.db.execute("CREATE TABLE users (id, name)")
        self.assertEqual(result, "Table users created.")

    def test_create_duplicate_table(self):
        self.db.execute("CREATE TABLE users (id, name)")
        with self.assertRaises(ValueError):
            self.db.execute("CREATE TABLE users (id, name)")

    def test_insert_into(self):
        self.db.execute("CREATE TABLE users (id, name)")
        result = self.db.execute("INSERT INTO users VALUES (1, 'Alice')")
        self.assertEqual(result, "1 row inserted into users.")

    def test_insert_into_unknown_table(self):
        with self.assertRaises(ValueError):
            self.db.execute("INSERT INTO users VALUES (1, 'Alice')")

    def test_insert_incorrect_number_of_columns(self): # TODO: This fails
        self.db.execute("CREATE TABLE users (id, name)")
        with self.assertRaises(ValueError):
            self.db.execute("INSERT INTO users (1, 'Alice', 'Bob')")

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

    def test_select_from_by_column(self):
        self.db.execute("CREATE TABLE users (id, name)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice')")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob')")
        result = self.db.execute("SELECT id FROM users")
        expected = [
            {'id': 1},
            {'id': 2}
        ]
        self.assertEqual(result, expected)

    def test_select_from_unknown_table(self):
        with self.assertRaises(ValueError):
            self.db.execute("SELECT * FROM users")

    def test_invalid_syntax(self):
        result = self.db.execute("syntax error")
        self.assertIn("syntax error", result.lower())

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)
