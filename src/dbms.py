import os
import pickle
from btree import BTree
from parser import parser
from ast_nodes import (
    CreateTableStatement,
    InsertStatement,
    SelectStatement,
    UpdateStatement,
    DeleteStatement,
)

class Database:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.tables = {}

    def execute(self, query):
        try:
            ast = parser.parse(query)
        except SyntaxError as e:
            return f"Syntax error: {e}"
        if isinstance(ast, CreateTableStatement):
            return self.create_table(ast)
        elif isinstance(ast, InsertStatement):
            return self.insert_into(ast)
        elif isinstance(ast, SelectStatement):
            return self.select_from(ast)
        elif isinstance(ast, UpdateStatement):
            return self.update_table(ast)
        elif isinstance(ast, DeleteStatement):
            return self.delete_from(ast)
        else:
            return "Unsupported SQL statement"

    def create_table(self, stmt):
        table_name = stmt.table_name
        columns = stmt.columns
        if not columns:
            raise ValueError("No columns specified")
        table = {'columns': columns}
        self.tables[table_name] = table
        self.save_table_meta(table_name)
        BTree(filename=os.path.join(self.data_dir, f"{table_name}.btree"))
        return f"Table {table_name} created."

    def insert_into(self, stmt):
        table_name = stmt.table_name
        values = stmt.values
        table = self.load_table_meta(table_name)
        if len(values) != len(table['columns']):
            raise ValueError("Column count doesn't match value count")
        # Parse values to appropriate data types
        parsed_values = [self.parse_value(val) for val in values]
        key = parsed_values[0]  # Ensure key is correctly typed
        row = dict(zip(table['columns'], parsed_values))
        btree = self.load_table_btree(table_name)
        btree.insert(key, row)
        return f"1 row inserted into {table_name}."

    def select_from(self, stmt):
        table_name = stmt.table_name
        columns = stmt.columns
        table = self.load_table_meta(table_name)
        btree = self.load_table_btree(table_name)
        if not columns or columns[0] == '*':
            selected_columns = table['columns']
        else:
            selected_columns = columns
        results = btree.traverse()
        result = [{col: row[col] for col in selected_columns} for key, row in results]
        return result

    def update_table(self, stmt):
        table_name = stmt.table_name
        set_clause = stmt.set_clause
        where_clause = stmt.where_clause
        table = self.load_table_meta(table_name)
        btree = self.load_table_btree(table_name)
        updated_rows = 0
        all_records = btree.traverse()
        where_value = self.parse_value(where_clause.value)
        set_value = self.parse_value(set_clause.value)
        for key, row in all_records:
            row_value = row[where_clause.column]
            if row_value == where_value:
                row[set_clause.column] = set_value
                btree.insert(key, row)  # This calls btree.save()
                updated_rows += 1
        return f"{updated_rows} rows updated in {table_name}."

    def delete_from(self, stmt):
        table_name = stmt.table_name
        where_clause = stmt.where_clause
        table = self.load_table_meta(table_name)
        btree = self.load_table_btree(table_name)
        deleted_rows = 0
        keys_to_delete = []
        # Parse where_clause value
        where_value = self.parse_value(where_clause.value)
        all_records = btree.traverse()
        for key, row in all_records:
            row_value = row[where_clause.column]
            if row_value == where_value:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            btree.delete(key)  # This calls btree.save()
            deleted_rows += 1
        return f"{deleted_rows} rows deleted from {table_name}."

    def parse_value(self, value):
        if isinstance(value, (int, float)):
            return value  # Value is already a number
        value = value.strip().strip("'")
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value  # Return as string if it cannot be converted

    def save_table_meta(self, table_name):
        table = self.tables.get(table_name)
        if table:
            with open(os.path.join(self.data_dir, f"{table_name}_meta.pkl"), 'wb') as f:
                pickle.dump(table, f)

    def load_table_meta(self, table_name):
        if table_name in self.tables:
            return self.tables[table_name]
        try:
            with open(os.path.join(self.data_dir, f"{table_name}_meta.pkl"), 'rb') as f:
                table = pickle.load(f)
                self.tables[table_name] = table
                return table
        except FileNotFoundError:
            raise ValueError(f"Table {table_name} does not exist.")

    def load_table_btree(self, table_name):
        filename = os.path.join(self.data_dir, f"{table_name}.btree")
        return BTree(filename=filename)
