import unittest
from parser import parser
from ast_nodes import (
    CreateTableStatement,
    InsertStatement,
    SelectStatement,
    UpdateStatement,
    DeleteStatement,
)

class TestSQLParser(unittest.TestCase):
    def test_create_table(self):
        query = "CREATE TABLE users (id, name)"
        ast = parser.parse(query)
        self.assertIsInstance(ast, CreateTableStatement)
        self.assertEqual(ast.table_name, 'users')
        self.assertEqual(ast.columns, ['id', 'name'])

    def test_insert_into(self):
        query = "INSERT INTO users VALUES (1, 'Alice')"
        ast = parser.parse(query)
        self.assertIsInstance(ast, InsertStatement)
        self.assertEqual(ast.table_name, 'users')
        self.assertEqual(ast.values, [1, 'Alice'])

    def test_select(self):
        query = "SELECT id, name FROM users"
        ast = parser.parse(query)
        self.assertIsInstance(ast, SelectStatement)
        self.assertEqual(ast.columns, ['id', 'name'])
        self.assertEqual(ast.table_name, 'users')

    def test_update(self):
        query = "UPDATE users SET name='Bob' WHERE id=1"
        ast = parser.parse(query)
        self.assertIsInstance(ast, UpdateStatement)
        self.assertEqual(ast.table_name, 'users')
        self.assertEqual(ast.set_clause.column, 'name')
        self.assertEqual(ast.set_clause.value, 'Bob')
        self.assertEqual(ast.where_clause.column, 'id')
        self.assertEqual(ast.where_clause.value, 1)

    def test_delete(self):
        query = "DELETE FROM users WHERE id=1"
        ast = parser.parse(query)
        self.assertIsInstance(ast, DeleteStatement)
        self.assertEqual(ast.table_name, 'users')
        self.assertEqual(ast.where_clause.column, 'id')
        self.assertEqual(ast.where_clause.value, 1)

    def test_invalid_syntax(self):
        query = "SELECT FROM users"
        with self.assertRaises(SyntaxError):
            parser.parse(query)
