# dbms.py

import os
import pickle
from btree import BTree

class Database:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.tables = {}

    def execute(self, query):
        tokens = query.strip().split()
        command = tokens[0].upper()

        if command == 'CREATE':
            return self.create_table(tokens)
        elif command == 'INSERT':
            return self.insert_into(tokens)
        elif command == 'SELECT':
            return self.select_from(tokens)
        elif command == 'UPDATE':
            raise NotImplementedError("UPDATE is not implemented in this version.")
        elif command == 'DELETE':
            raise NotImplementedError("DELETE is not implemented in this version.")
        else:
            raise ValueError(f"Unknown command: {command}")

    def create_table(self, tokens):
        if tokens[1].upper() != 'TABLE':
            raise ValueError("Syntax error in CREATE TABLE")
        table_name = tokens[2]
        columns_str = ' '.join(tokens[3:])
        if columns_str.startswith('(') and columns_str.endswith(')'):
            columns_str = columns_str[1:-1]
        else:
            raise ValueError("Columns should be enclosed in parentheses")
        columns = columns_str.split(',')
        columns = [col.strip() for col in columns if col.strip()]
        if not columns:
            raise ValueError("No columns specified")
        table = {'columns': columns}
        self.tables[table_name] = table
        self.save_table_meta(table_name)
        # Initialize an empty B-tree for the table
        BTree(filename=os.path.join(self.data_dir, f"{table_name}.btree"))
        return f"Table {table_name} created."

    def insert_into(self, tokens):
        if tokens[1].upper() != 'INTO':
            raise ValueError("Syntax error in INSERT INTO")
        table_name = tokens[2]
        if 'VALUES' not in tokens:
            raise ValueError("VALUES keyword missing in INSERT INTO")
        values_index = tokens.index('VALUES')
        values_str = ' '.join(tokens[values_index + 1:])
        if values_str.startswith('(') and values_str.endswith(')'):
            values_str = values_str[1:-1]
        else:
            raise ValueError("Values should be enclosed in parentheses")
        values = values_str.split(',')
        values = [val.strip().strip("'") for val in values if val.strip()]
        table = self.load_table_meta(table_name)
        if len(values) != len(table['columns']):
            raise ValueError("Column count doesn't match value count")
        # Use the first column as the key
        key = values[0]
        row = dict(zip(table['columns'], values))
        btree = self.load_table_btree(table_name)
        btree.insert(key, row)
        return f"1 row inserted into {table_name}."

    def select_from(self, tokens):
        if 'FROM' not in tokens:
            raise ValueError("Syntax error in SELECT")
        select_index = tokens.index('SELECT')
        from_index = tokens.index('FROM')
        columns_str = ' '.join(tokens[select_index + 1:from_index])
        columns = columns_str.split(',')
        columns = [col.strip() for col in columns if col.strip()]
        table_name = tokens[from_index + 1]
        table = self.load_table_meta(table_name)
        btree = self.load_table_btree(table_name)
        if not columns or columns[0] == '*':
            selected_columns = table['columns']
        else:
            selected_columns = columns
        results = btree.traverse()
        result = [{col: row[col] for col in selected_columns} for key, row in results]
        return result

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
