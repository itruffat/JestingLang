import ply.yacc as yacc
import ply.lex as lex
from JestingLang.Core.JParsing.JestingAST import *
from JestingLang.JestingScript.JParsing.JestingScriptAST import *
from JestingLang.Misc.JLogic.LogicFunctions import address_regex_str

def subtokenIsType(tokens, position, checkType):
    return tokens.slice[position].type == checkType


class LexerParser:

    def __init__(self, *, multilineScript = False):

        self.multilineScript = multilineScript
        self.spreadsheet_function_set = ( 'MOD' , )
        self.implemented_functions = ('IF', 'INDIRECT', 'NOT', 'AND', 'OR')
        self.tokens = (
                     'CELL_ADDRESS', 'NUMBER', 'BOOLEAN',
                     'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'BIGGER', 'SMALLER',
                     'LPAREN', 'RPAREN', 'AMPERSAND', 'STRING', 'COMMA'
                 ) + self.implemented_functions + self.spreadsheet_function_set + ('TEXT',)
        if self.multilineScript:
            self.tokens += ('ASSIGN_FORMULA', 'ASSIGN_VALUE', 'UNASSIGN', 'TICK',
                            'SETDEFAULTS', 'PRINT', 'PRINTALL', 'NEWLINE', 'COMMENT','OPEN', 'CLOSE', )
        self.setup_tokens()
        self.lexer = self.jesting_lexer()
        self.parser = self.jesting_parser()
        self.clearup_tokens()

    def setup_tokens(self):
        global tokens

        self.undefined_token = object()
        self.old_tokens = tokens if "tokens" in globals() else self.undefined_token
        tokens = self.tokens

    def clearup_tokens(self):
        global tokens

        tokens = self.old_tokens
        if tokens is self.undefined_token:
            del tokens
        del self.old_tokens
        del self.undefined_token

    def jesting_lexer(self):

        #t_STRING = r'"[^"]*"'
        def t_STRING(t):
            r'("[^"]*")|(\'[^\']*\')'
            t.value = t.value[1:-1]
            return t

        # ~~~ START OF MULTILINE

        if self.multilineScript:
            t_ASSIGN_FORMULA = r'@='
            #t_ASSIGN_VALUE = r'@\s[^\n]+'
            def t_ASSIGN_VALUE(t):
                r'@\s[^\n]+'
                t.value = t.value[2:]
                return t
            t_UNASSIGN = r'@'
            t_TICK = r'~+'
            t_SETDEFAULTS=r':'
            t_PRINTALL=r'!!'
            t_PRINT=r'!'
            #t_COMMENT=r'//[^\n]*'
            def t_COMMENT(t):
                r'//[^\n]*'
                t.value = t.value[2:]
                return t
            #t_OPEN=r'}[^\n]*'
            def t_OPEN(t):
                r'}[^\n]*'
                t.value = f"[{t.value[1:].strip()}]"
                return t
            #t_CLOSE=r'{[^\n]*'
            def t_CLOSE(t):
                r'{[^\n]*'
                t.value = f"[{t.value[1:].strip()}]"
                return t

        # ~~~ END OF MULTILINE

        t_PLUS = r'\+'
        t_MINUS = r'-'
        t_TIMES = r'\*'
        t_DIVIDE = r'/'
        t_EQUALS = r'='
        t_BIGGER = r'>'
        t_SMALLER= r'<'
        t_LPAREN = r'\('
        t_RPAREN = r'\)'
        t_AMPERSAND = r'&'
        t_COMMA = r'\,'
        t_MOD = r'MOD'

        def t_CELL_ADDRESS(t):
            return t

        t_CELL_ADDRESS.__doc__ = address_regex_str  # This needs to be shared from another file

        def t_NUMBER(t):
            r'\d+'
            try:
                t.value = int(t.value)
            except ValueError:
                print("Integer value too large %d", t.value)
                t.value = 0
            return t

        def t_TEXT(t):
            r'[a-zA-Z_][a-zA-Z_0-9]*'
            if t.value in self.implemented_functions:
                t.type = t.value
            if t.value in ('TRUE', 'FALSE'):
                t.type = 'BOOLEAN'
            return t

        def t_NEWLINE(t):
            r'\n[\n 	]*'
            t.lexer.lineno += t.value.count("\n")
            if self.multilineScript:
                t.value = "\n"
            else:
                t = None
            return t

        def t_error(t):
            print("Illegal character '%s'" % t.value[0])
            t.lexer.skip(1)

        t_ignore = " \t"

        lexer = lex.lex()

        return lexer

    def jesting_parser(self):

        # Parsing rules

        precedence = (
            ('nonassoc', 'EQUALS'),
            ('left', 'PLUS', 'MINUS', 'AMPERSAND'),
            ('left', 'TIMES', 'DIVIDE'),
            ('right', 'UMINUS')
        )

        # ~~~ START OF MULTILINE

        if self.multilineScript:

            def p_start(t):
                '''start : lines
                        | NEWLINE lines
                '''

                if len(t) == 2:
                    t[0] = t[1]
                elif len(t) == 3:
                    t[0] = t[2]
                if t[0] is None:
                    raise Exception("Empty program")
                return t[0]

            def p_lines(t):
                '''lines : line
                         | lines NEWLINE line
                '''

                if len(t) == 2:
                    if t[1] is None:
                        t[0] = None
                    else:
                        t[0] = ScriptNode(t[1])
                elif len(t) == 4:
                    if t[3] is None:
                        t[0] = t[1]
                    elif t[1] is None:
                        t[0] = ScriptNode(t[3])
                    else:
                        t[0] = t[1].addChild(t[3])
                return t[0]

            def p_line(t):
                '''line :
                        | COMMENT
                        | TICK
                        | PRINTALL
                        | PRINT CELL_ADDRESS
                        | OPEN
                        | CLOSE
                        | SETDEFAULTS CELL_ADDRESS
                        | CELL_ADDRESS UNASSIGN
                        | CELL_ADDRESS ASSIGN_VALUE
                        | PRINT EQUALS CELL_ADDRESS
                        | CELL_ADDRESS ASSIGN_FORMULA statement
                '''

                if len(t) == 2:

                    if subtokenIsType(t,1,"PRINTALL"):
                    #if t[1] == "!!":
                        t[0] = PrintValueNode(print_all=True)
                    elif subtokenIsType(t, 1, "TICK"):
                    #elif t[1] == "~":
                        t[0] = TickNode(len(t[1]))
                    elif subtokenIsType(t, 1, "OPEN"):
                    #elif t[1][0] == "}":
                        t[0] = OpenCloseFileNode(t[1], do_open=True)
                    elif subtokenIsType(t, 1, "CLOSE"):
                    #elif t[1][0] == "{":
                        t[0] = OpenCloseFileNode(t[1], do_open=False)
                    else:
                        t[0] = None

                elif len(t) == 3:
                    if subtokenIsType(t,1,"SETDEFAULTS"):
                    #if t[1] == ":":
                        t[0] = SetDefaultsNode(t[2])
                    elif subtokenIsType(t, 1, "PRINT"):
                    #elif t[1] == "!":
                        t[0] = PrintValueNode(cell=t[2], print_value=True)
                    elif subtokenIsType(t, 2, "UNASSIGN"):
                    #elif t[2] == "@":
                        t[0] = AssignNode(t[1], EmptyValueNode())
                    else:
                        t[0] = AssignNode(t[1], RawInputNode(t[2]))

                elif len(t) == 4:
                    if subtokenIsType(t,2,"EQUALS"):
                        t[0] = PrintValueNode(cell=t[3], print_value=False)
                    else:
                        t[0] = AssignNode(t[1], t[3])

                return t[0]

        # ~~~ END OF MULTILINE

        def p_statement(t):
            '''statement    : parameter
                            | callable_operation
                            | fixed_operation
            '''
            t[0] = t[1]
            return t[0]

        def p_callable_opereation(t):
            '''callable_operation   : IF LPAREN statement COMMA  statement COMMA statement RPAREN
                                    | NOT LPAREN statement RPAREN
                                    | AND LPAREN statement COMMA statement RPAREN
                                    | OR LPAREN statement COMMA statement RPAREN
                                    | INDIRECT LPAREN statement RPAREN
                                    | TEXT LPAREN statement RPAREN
                                    | TEXT LPAREN statement COMMA statement RPAREN
                                    | TEXT LPAREN statement COMMA statement COMMA statement RPAREN '''
            if subtokenIsType(t, 1, "NOT"):
            #if t[1] == 'NOT':
                t[0] = OperationNode(t[1], {0: t[3]})
            if subtokenIsType(t, 1, "AND") or subtokenIsType(t, 1, "OR"):
            #if t[1] in ('AND', 'OR'):
                t[0] = OperationNode(t[1], {0: t[3], 1: t[5]})
            if subtokenIsType(t, 1, "IF"):
            #if t[1] == 'IF':
                t[0] = IfNode(t[3], t[5], t[7])
            if subtokenIsType(t, 1, "INDIRECT"):
            #if t[1] == 'INDIRECT':
                t[0] = IndirectNode(t[3])
            if subtokenIsType(t, 1, "TEXT"):
                if t[1] not in self.spreadsheet_function_set:
                    raise Exception("unknown text")
                if len(t) == 5:
                    t[0] = OperationNode(t[1], {0: t[3]})
                elif len(t) == 7:
                    t[0] = OperationNode(t[1], {0: t[3], 1: t[5]})
                elif len(t) == 9:
                    t[0] = OperationNode(t[1], {0: t[3], 1: t[5], 2: t[7]})
                else:
                    raise Exception("unknown call")
            return t[0]


        def p_statement_paren(t):
            '''statement    :  LPAREN statement RPAREN '''
            t[0] = t[2]
            return t[0]


        def p_fixed_operation(t):
            '''fixed_operation  : statement EQUALS statement
                                | statement AMPERSAND statement
                                | statement PLUS statement
                                | statement MINUS statement
                                | statement TIMES statement
                                | statement DIVIDE statement
                                | statement SMALLER BIGGER statement
                                | statement BIGGER statement
                                | statement SMALLER statement
                                | statement BIGGER EQUALS statement
                                | statement SMALLER EQUALS statement
                                | MINUS statement %prec UMINUS '''
            if t[1] == "-":
                t[0] = OperationNode("u-", {0: t[2]})
            elif t[2] in ['<', '>']:
                if t[2] == '<' and t[3] == '>':
                    equals = OperationNode('=', {0: t[1], 1: t[4]})
                    t[0] = OperationNode('NOT', {0: equals})
                else:
                    second = t[4] if t[3] == '=' else t[3]
                    if t[2] == '>':
                        bg, sm = (t[1], second)
                    else:
                        bg, sm = (second, t[1])  # IN CASE ITS SMALLER JUST REVERSE THE ORDER
                    bigger = OperationNode('>', {0: bg, 1: sm})
                    if t[3] == '=':
                        equals = OperationNode('=', {0: bg, 1: sm})
                        t[0] = OperationNode('OR', {0: equals, 1: bigger})
                    else:
                        t[0] = bigger
            else:
                t[0] = OperationNode(t[2], {0: t[1], 1: t[3]})
            return t[0]


        def p_parameter_int(t):
            '''parameter    : NUMBER'''
            t[0] = IntValueNode(t[1])
            return t[0]


        def p_parameter_STR(t):
            '''parameter    : STRING'''
            t[0] = StrValueNode(t[1])
            return t[0]


        def p_parameter_ADDRESS(t):
            '''parameter    : CELL_ADDRESS'''
            t[0] = ReferenceValueNode(t[1])
            return t[0]


        def p_parameter_BOOL(t):
            '''parameter    : BOOLEAN'''
            t[0] = BoolValueNode(t[1])
            return t[0]


        def p_text_parameter_text(t):
            '''statement     : TEXT'''
            text = t[1]
            text = text.upper()
            text = text.replace(".", "_")
            text = text if text != "error" else "_error"
            if text in self.spreadsheet_function_set:
                raise Exception(f"FUNCTION '{t[1]}' NOT IMPLEMENTED")
            else:
                raise Exception(f"'{t[1]}' is Unknown")


        def p_error(t):
            print("Syntax error at '%s'" % t.value)

        parser = yacc.yacc(tabmodule="LexerParser_cachedParseTable", debug=False)
        return parser
