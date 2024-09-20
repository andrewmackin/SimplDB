import ply.lex as lex

# Reserved words
reserved = {
    'create': 'CREATE',
    'table': 'TABLE',
    'insert': 'INSERT',
    'into': 'INTO',
    'values': 'VALUES',
    'select': 'SELECT',
    'from': 'FROM',
    'update': 'UPDATE',
    'set': 'SET',
    'where': 'WHERE',
    'delete': 'DELETE',
}

# List of token names
tokens = [
    'IDENTIFIER',
    'STRING',
    'NUMBER',
    'COMMA',
    'LPAREN',
    'RPAREN',
    'EQ',
    'TIMES',
] + list(reserved.values())

# Regular expression rules for simple tokens
t_COMMA    = r','
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_EQ       = r'='
t_TIMES    = r'\*'

# Ignore spaces and tabs
t_ignore = ' \t'

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')
    return t

def t_STRING(t):
    r"'([^']*)'"
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    pass

def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}' at position {t.lexpos}")

lexer = lex.lex()
