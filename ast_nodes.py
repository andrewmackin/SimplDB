# ast_nodes.py

class SQLStatement:
    pass

class CreateTableStatement(SQLStatement):
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.columns = columns

class InsertStatement(SQLStatement):
    def __init__(self, table_name, values):
        self.table_name = table_name
        self.values = values

class SelectStatement(SQLStatement):
    def __init__(self, columns, table_name):
        self.columns = columns
        self.table_name = table_name
