import unittest
import shutil
import os
from dbms import Database

class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.data_dir = 'test_data_persistence'
        shutil.rmtree(self.data_dir, ignore_errors=True)
        os.makedirs(self.data_dir, exist_ok=True)
        self.db = Database(data_dir=self.data_dir)

    def test_update_persistence(self):
        self.db.execute("CREATE TABLE users (id, name)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice')")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob')")

        self.db.execute("UPDATE users SET name='Charlie' WHERE id=2")

        db_new = Database(data_dir=self.data_dir)
        result = db_new.execute("SELECT * FROM users")
        expected = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Charlie'}]
        self.assertEqual(result, expected, "Update persistence test failed.")

    def test_delete_persistence(self):
        self.db.execute("CREATE TABLE users (id, name)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice')")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob')")

        self.db.execute("DELETE FROM users WHERE id=1")

        db_new = Database(data_dir=self.data_dir)
        result = db_new.execute("SELECT * FROM users")
        expected = [{'id': 2, 'name': 'Bob'}]
        self.assertEqual(result, expected, "Delete persistence test failed.")

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
