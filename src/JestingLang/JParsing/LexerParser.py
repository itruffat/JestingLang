import ply.yacc as yacc
import ply.lex as lex

from JestingLang.JParsing.JestingAST import *
from JestingLang.JParsing.JestingScriptAST import *

class LexerParser:

    def __init__(self, *, multilineScript = False):

        self.multilineScript = multilineScript
        self.spreadsheet_function_set = {}
        self.implemented_functions = ('IF', 'INDIRECT', 'NOT', 'AND', 'OR')
        self.tokens = (
                     'CELL_ADDRESS', 'NUMBER', 'BOOLEAN',
                     'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'BIGGER', 'SMALLER',
                     'LPAREN', 'RPAREN', 'AMPERSAND', 'STRING', 'COMMA'
                 ) + self.implemented_functions + ('TEXT',)
        if self.multilineScript:
            self.tokens += ('ASSIGN_FORMULA', 'ASSIGN_VALUE', 'UNASSIGN', 'TICK',
                            'SETDEFAULTS', 'PRINT', 'PRINTALL', 'NEWLINE', 'COMMENT', )
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

        t_STRING = r'"[^"]*"'

        # ~~~ START OF MULTILINE

        if self.multilineScript:
            t_ASSIGN_VALUE = r'@[^=\n][^\n]*'
            t_ASSIGN_FORMULA = r'@='
            t_UNASSIGN = r'@'
            t_TICK = r'\'+'
            t_SETDEFAULTS=r':'
            t_PRINTALL=r'!!'
            t_PRINT=r'!'
            t_COMMENT=r'//[^\n]*'

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

        def t_CELL_ADDRESS(t):
            r'(?P<path>(?P<workbook>\[[a-zA-Z0-9\.\(\)]+\])?(?P<worksheet>[a-zA-Z][a-zA-Z0-9]*!))?\$?(?P<initial>([a-z]+|[A-Z]+)\$?[0-9]+)(?P<final>:\$?[a-zA-Z]+\$?[0-9]+)?'
            return t


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
                        | SETDEFAULTS CELL_ADDRESS
                        | CELL_ADDRESS UNASSIGN
                        | CELL_ADDRESS ASSIGN_VALUE
                        | CELL_ADDRESS ASSIGN_FORMULA statement
                '''

                if len(t) == 2:

                    if t[1] == "!!":
                        t[0] = PrintValueNode(print_all=True)
                    elif t[1] == "'":
                        t[0] = TickNode(len(t[1]))
                    else:
                        t[0] = None

                elif len(t) == 3:
                    if t[1] == ":":
                        t[0] = SetDefaultsNode(t[2])
                    elif t[1] == "!":
                        t[0] = PrintValueNode(cell=t[2])
                    elif t[2] == "@":
                        t[0] = AssignNode(t[1], EmptyValueNode())
                    else:
                        t[0] = AssignNode(t[1], RawInputNode(t[2]))

                elif len(t) == 4:
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
                                    | INDIRECT LPAREN statement RPAREN '''
            if t[1] == 'NOT':
                t[0] = OperationNode(t[1], {0: t[3]})
            if t[1] in ('AND', 'OR'):
                t[0] = OperationNode(t[1], {0: t[3], 1: t[5]})
            if t[1] == 'IF':
                t[0] = IfNode(t[3], t[5], t[7])
            if t[1] == 'INDIRECT':
                t[0] = IndirectNode(t[3])

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
            t[0] = StrValueNode(t[1][1:-1])
            return t[0]


        def p_parameter_ADDRESS(t):
            '''parameter    : CELL_ADDRESS'''
            t[0] = ReferenceValueNode(t[1])
            return t[0]


        def p_parameter_BOOL(t):
            '''parameter    : BOOLEAN'''
            t[0] = BoolValueNode(t[1])
            return t[0]


        def p_parameter_text(t):
            '''parameter     : TEXT'''
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


lexerparser = LexerParser()

lexer = lexerparser.lexer

parser = lexerparser.parser

