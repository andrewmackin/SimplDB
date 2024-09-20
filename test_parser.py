# test_parser.py

import unittest
from parser import SQLParser
from ast_nodes import CreateTableStatement, InsertStatement, SelectStatement

class TestSQLParser(unittest.TestCase):
    def setUp(self):
        self.parser = SQLParser()

    def test_parse_create_table(self):
        query = "CREATE TABLE users (id, name)"
        ast = self.parser.parse(query)
        self.assertIsInstance(ast, CreateTableStatement)
        self.assertEqual(ast.table_name, 'users')
        self.assertEqual(ast.columns, ['id', 'name'])

    def test_parse_create_table_with_extra_spaces(self):
        query = "CREATE    TABLE    users    (   id   ,   name   )"
        ast = self.parser.parse(query)
        self.assertIsInstance(ast, CreateTableStatement)
        self.assertEqual(ast.table_name, 'users')
        self.assertEqual(ast.columns, ['id', 'name'])

    def test_parse_insert_into(self):
        query = "INSERT INTO users VALUES (1, 'Alice')"
        ast = self.parser.parse(query)
        self.assertIsInstance(ast, InsertStatement)
        self.assertEqual(ast.table_name, 'users')
        self.assertEqual(ast.values, ['1', 'Alice'])

    def test_parse_insert_with_string_containing_spaces(self):
        query = "INSERT INTO users VALUES (1, 'Alice Smith')"
        ast = self.parser.parse(query)
        self.assertIsInstance(ast, InsertStatement)
        self.assertEqual(ast.values, ['1', 'Alice Smith'])

    def test_parse_select_all(self):
        query = "SELECT * FROM users"
        ast = self.parser.parse(query)
        self.assertIsInstance(ast, SelectStatement)
        self.assertEqual(ast.columns, ['*'])
        self.assertEqual(ast.table_name, 'users')

    def test_parse_select_specific_columns(self):
        query = "SELECT id, name FROM users"
        ast = self.parser.parse(query)
        self.assertIsInstance(ast, SelectStatement)
        self.assertEqual(ast.columns, ['id', 'name'])
        self.assertEqual(ast.table_name, 'users')

    def test_parse_select_with_extra_spaces(self):
        query = "SELECT   id  ,   name    FROM    users"
        ast = self.parser.parse(query)
        self.assertIsInstance(ast, SelectStatement)
        self.assertEqual(ast.columns, ['id', 'name'])
        self.assertEqual(ast.table_name, 'users')

    def test_parse_invalid_query(self):
        query = "DROP TABLE users"
        with self.assertRaises(ValueError):
            self.parser.parse(query)

    def test_parse_empty_query(self):
        query = ""
        with self.assertRaises(ValueError):
            self.parser.parse(query)

    def test_parse_create_table_missing_parentheses(self):
        query = "CREATE TABLE users id, name"
        with self.assertRaises(ValueError):
            self.parser.parse(query)

    def test_parse_insert_missing_values(self):
        query = "INSERT INTO users (1, 'Alice')"
        with self.assertRaises(ValueError):
            self.parser.parse(query)

    def test_parse_select_missing_from(self):
        query = "SELECT id, name users"
        with self.assertRaises(ValueError):
            self.parser.parse(query)

if __name__ == '__main__':
    unittest.main()
