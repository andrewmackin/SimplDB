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
        self.tables_meta = os.path.join(self.data_dir, 'tables_meta.pkl')
        if os.path.exists(self.tables_meta):
            with open(self.tables_meta, 'rb') as f:
                self.tables = pickle.load(f)
        else:
            self.tables = {}
            with open(self.tables_meta, 'wb') as f:
                pickle.dump(self.tables, f)
        # Cache btree instances
        self.btrees = {}

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
        if table_name in self.tables:
            raise ValueError(f"Table {table_name} already exists.")
        # Initialize BTree for the table
        storage_path = os.path.join(self.data_dir, table_name)
        BTree(t=3, storage_path=storage_path)
        self.tables[table_name] = {
            'columns': columns,
            'btree_path': storage_path
        }
        # Save metadata
        with open(self.tables_meta, 'wb') as f:
            pickle.dump(self.tables, f)
        return f"Table {table_name} created."

    def get_btree(self, table_name):
        if table_name not in self.btrees:
            table = self.tables.get(table_name)
            if not table:
                raise ValueError(f"Table {table_name} does not exist.")
            btree = BTree(t=3, storage_path=table['btree_path'])
            self.btrees[table_name] = btree
        return self.btrees[table_name]

    def insert_into(self, stmt):
        table_name = stmt.table_name
        values = stmt.values
        table = self.tables.get(table_name)
        if not table:
            raise ValueError(f"Table {table_name} does not exist.")
        if len(values) != len(table['columns']):
            raise ValueError("Column count doesn't match value count")
        # Parse values to appropriate data types
        parsed_values = [self.parse_value(val) for val in values]
        key = parsed_values[0]  # Assuming first column is the primary key
        row = dict(zip(table['columns'], parsed_values))
        btree = self.get_btree(table_name)
        btree.insert(key, row)
        return f"1 row inserted into {table_name}."


    def select_from(self, stmt):
        table_name = stmt.table_name
        columns = stmt.columns
        table = self.tables.get(table_name)
        if not table:
            raise ValueError(f"Table {table_name} does not exist.")
        btree = self.get_btree(table_name)
        all_records = btree.traverse()
        if columns == ['*']:
            return [record for _, record in all_records]
        else:
            selected = []
            for _, record in all_records:
                selected_record = {col: record[col] for col in columns}
                selected.append(selected_record)
            return selected


    def update_table(self, stmt):
        table_name = stmt.table_name
        set_clause = stmt.set_clause
        where_clause = stmt.where_clause
        table = self.tables.get(table_name)
        if not table:
            raise ValueError(f"Table {table_name} does not exist.")
        btree = self.get_btree(table_name)
        updated_rows = 0
        all_records = btree.traverse()
        where_value = self.parse_value(where_clause.value)
        set_value = self.parse_value(set_clause.value)
        for key, row in all_records:
            row_value = row[where_clause.column]
            if row_value == where_value:
                row[set_clause.column] = set_value
                btree.insert(key, row)  # Update the record
                updated_rows += 1
        return f"{updated_rows} rows updated in {table_name}."

    def delete_from(self, stmt):
        table_name = stmt.table_name
        where_clause = stmt.where_clause
        table = self.tables.get(table_name)
        if not table:
            raise ValueError(f"Table {table_name} does not exist.")
        btree = self.get_btree(table_name)
        deleted_rows = 0
        keys_to_delete = []
        all_records = btree.traverse()
        # Parse where_clause value
        where_value = self.parse_value(where_clause.value)

        for key, row in all_records:
            row_value = row[where_clause.column]
            if row_value == where_value:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            btree.delete(key)
            deleted_rows += 1
        return f"{deleted_rows} rows deleted from {table_name}."


    def parse_value(self, value):
        if isinstance(value, (int, float)):
            return value
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
