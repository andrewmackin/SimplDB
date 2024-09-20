import ply.yacc as yacc
from lexer import tokens  # Import tokens from lexer
from ast_nodes import (
    CreateTableStatement,
    InsertStatement,
    SelectStatement,
    UpdateStatement,
    DeleteStatement,
    WhereClause,
    SetClause,
)

# TODO: Precedence rules
precedence = ()

def p_statement(p):
    '''statement : create_table_statement
                 | insert_statement
                 | select_statement
                 | update_statement
                 | delete_statement'''
    p[0] = p[1]

def p_create_table_statement(p):
    'create_table_statement : CREATE TABLE IDENTIFIER LPAREN column_list RPAREN'
    p[0] = CreateTableStatement(table_name=p[3], columns=p[5])

def p_column_list(p):
    '''column_list : column_list COMMA IDENTIFIER
                   | IDENTIFIER'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_insert_statement(p):
    'insert_statement : INSERT INTO IDENTIFIER VALUES LPAREN value_list RPAREN'
    p[0] = InsertStatement(table_name=p[3], values=p[6])

def p_value_list(p):
    '''value_list : value_list COMMA value
                  | value'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_value(p):
    '''value : STRING
             | NUMBER'''
    p[0] = p[1]

def p_select_statement(p):
    'select_statement : SELECT select_list FROM IDENTIFIER'
    p[0] = SelectStatement(columns=p[2], table_name=p[4])

def p_select_list(p):
    '''select_list : select_list COMMA IDENTIFIER
                   | IDENTIFIER
                   | TIMES'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif p[1] == '*':
        p[0] = ['*']
    else:
        p[0] = [p[1]]

def p_update_statement(p):
    'update_statement : UPDATE IDENTIFIER SET set_clause where_clause'
    p[0] = UpdateStatement(table_name=p[2], set_clause=p[4], where_clause=p[5])

def p_set_clause(p):
    'set_clause : IDENTIFIER EQ value'
    p[0] = SetClause(column=p[1], value=p[3])

def p_delete_statement(p):
    'delete_statement : DELETE FROM IDENTIFIER where_clause'
    p[0] = DeleteStatement(table_name=p[3], where_clause=p[4])

def p_where_clause(p):
    'where_clause : WHERE IDENTIFIER EQ value'
    p[0] = WhereClause(column=p[2], value=p[4])

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}'")
    else:
        raise SyntaxError("Syntax error at EOF")

parser = yacc.yacc()
