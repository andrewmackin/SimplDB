# parser.py

from ast_nodes import CreateTableStatement, InsertStatement, SelectStatement

class SQLParser:
    def parse(self, query):
        tokens = self.tokenize(query)
        if not tokens:
            raise ValueError("Empty query")
        command = tokens[0].upper()
        if command == 'CREATE':
            return self.parse_create_table(tokens)
        elif command == 'INSERT':
            return self.parse_insert_into(tokens)
        elif command == 'SELECT':
            return self.parse_select(tokens)
        else:
            raise ValueError(f"Unknown command: {command}")

    def tokenize(self, query):
        # Simple tokenizer; for a full SQL parser, use a lexer/parser generator
        tokens = []
        token = ''
        in_string = False
        for char in query:
            if char == "'" and not in_string:
                in_string = True
                if token:
                    tokens.append(token)
                    token = ''
                token += char
            elif char == "'" and in_string:
                in_string = False
                token += char
                tokens.append(token)
                token = ''
            elif in_string:
                token += char
            elif char in ' (),':
                if token:
                    tokens.append(token)
                    token = ''
                if char.strip():
                    tokens.append(char)
            else:
                token += char
        if token:
            tokens.append(token)
        return tokens

    def parse_create_table(self, tokens):
        if tokens[1].upper() != 'TABLE':
            raise ValueError("Expected TABLE keyword after CREATE")
        table_name = tokens[2]
        if tokens[3] != '(' or tokens[-1] != ')':
            raise ValueError("Expected parentheses around column definitions")
        columns = tokens[4:-1]
        columns = [col for col in columns if col != ',']
        return CreateTableStatement(table_name, columns)

    def parse_insert_into(self, tokens):
        if tokens[1].upper() != 'INTO':
            raise ValueError("Expected INTO keyword after INSERT")
        table_name = tokens[2]
        if 'VALUES' not in tokens:
            raise ValueError("Expected VALUES keyword in INSERT statement")
        values_index = tokens.index('VALUES')
        if tokens[values_index + 1] != '(' or tokens[-1] != ')':
            raise ValueError("Expected parentheses around VALUES")
        values = tokens[values_index + 2:-1]
        values = [val.strip("'") for val in values if val != ',']
        return InsertStatement(table_name, values)

    def parse_select(self, tokens):
        if 'FROM' not in tokens:
            raise ValueError("Expected FROM keyword in SELECT statement")
        from_index = tokens.index('FROM')
        columns = tokens[1:from_index]
        columns = [col for col in columns if col != ',']
        table_name = tokens[from_index + 1]
        return SelectStatement(columns, table_name)
