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

class UpdateStatement(SQLStatement):
    def __init__(self, table_name, set_clause, where_clause):
        self.table_name = table_name
        self.set_clause = set_clause
        self.where_clause = where_clause

class DeleteStatement(SQLStatement):
    def __init__(self, table_name, where_clause):
        self.table_name = table_name
        self.where_clause = where_clause

class SetClause:
    def __init__(self, column, value):
        self.column = column
        self.value = value

class WhereClause:
    def __init__(self, column, value):
        self.column = column
        self.value = value
