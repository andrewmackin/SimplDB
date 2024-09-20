# dbms.py

import os
import pickle
from btree import BTree
from parser import SQLParser
from ast_nodes import CreateTableStatement, InsertStatement, SelectStatement

class Database:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.tables = {}
        self.parser = SQLParser()

    def execute(self, query):
        ast = self.parser.parse(query)
        if isinstance(ast, CreateTableStatement):
            return self.create_table(ast)
        elif isinstance(ast, InsertStatement):
            return self.insert_into(ast)
        elif isinstance(ast, SelectStatement):
            return self.select_from(ast)
        else:
            raise ValueError("Unsupported SQL statement")

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
        key = values[0]
        row = dict(zip(table['columns'], values))
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
