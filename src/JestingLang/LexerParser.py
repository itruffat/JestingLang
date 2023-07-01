import ply.yacc as yacc
import ply.lex as lex
from JestingLang.Core.JParsing.JestingAST import *
from JestingLang.JestingScript.JParsing.JestingScriptAST import *
from JestingLang.JestingScript.JFileLoader.ExternalFileLoader import ExternalFileLoader
from JestingLang.Misc.JLogic.LogicFunctions import address_regex_str, address

class LexerParserException(Exception):
    def __init__(self, t):
        self.t = t

class UntokenizableCodeException(LexerParserException):
    pass

class UnparsableCodeException(LexerParserException):
    pass

def getTokenType(tokens, position):
    return tokens.slice[position].type

def subtokenIsType(tokens, position, checkType):
    return getTokenType(tokens, position) == checkType

class LexerParser:

    def __init__(self, *, multilineScript = False, useCellToken=False, external_file_loader = None):

        self.multilineScript = multilineScript
        self.useCellToken = useCellToken
        self.spreadsheet_function_set = {'MOD': 2}  # second value is amount of operands it receives
        self.fixed_implementations = ('IF', 'INDIRECT',)
        self.logic_functions = ('NOT', 'AND', 'OR',)
        self.fixed_operations = ('PLUS', 'MINUS', 'TIMES',
                                      'DIVIDE', 'EQUALS', 'BIGGER', 'AMPERSAND',)
        self.indirect_fixed_operations = ('SMALLER',)
        self.tokens = (
                     'CELL_ADDRESS', 'NUMBER', 'BOOLEAN',
                     'LPAREN', 'RPAREN', 'STRING', 'COMMA'
                 ) + self.fixed_implementations + self.logic_functions \
                      + self.indirect_fixed_operations + self.fixed_operations + ('TEXT',)
        if self.multilineScript:
            self.tokens += ('RIGHT_LEFT_ASSIGN', 'ASSIGN_VALUE', 'LEFT_RIGHT_ASSIGN', 'ASSIGN_ALIAS', 'TICK',
                            'SETDEFAULTS', 'PRINT', 'NEWLINE', 'COMMENT',
                            'OPEN', 'CLOSE', 'INCLUDE_EXTERNAL_FILE', 'RULE_INDICATOR', 'LOCK', 'UNLOCK', )
            self.external_file_loader = \
                external_file_loader if external_file_loader is not None else ExternalFileLoader()
        self.setup_tokens()
        self.lexer = self.jesting_lexer()
        self.parser = self.jesting_parser()
        self.clearup_tokens()

    def parse(self, code, *, needs_fresh_lexer = False):
        tmp_lexer = self.lexer.clone() if needs_fresh_lexer else self.lexer  # Allows multiple parsings at once
        return self.parser.parse(code, lexer=tmp_lexer)

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

            t_INCLUDE_EXTERNAL_FILE = r'\*INCLUDE\*'
            t_RULE_INDICATOR = r'\#'
            t_ASSIGN_ALIAS=r'\?'
            t_RIGHT_LEFT_ASSIGN = r'<~'
            def t_ASSIGN_VALUE(t):
                r'<<\s[^\n]+'
                t.value = t.value[3:]
                return t
            t_LEFT_RIGHT_ASSIGN = r'~>'
            t_TICK = r';+'
            t_SETDEFAULTS=r'@'
            t_PRINT=r'!'
            def t_COMMENT(t):
                r'//[^\n]*'
                t.value = t.value[2:]
                return t
            def t_OPEN(t):
                r'}[ 	]*[^ 	\n]+[ 	]*'
                t.value = f"[{t.value[1:].strip()}]"
                return t
            def t_CLOSE(t):
                r'{[ 	]*[^ 	\n]+[ 	]*'
                t.value = f"[{t.value[1:].strip()}]"
                return t
            t_LOCK=r"\(\+\)"
            t_UNLOCK=r"\(-\)"
            def t_NEWLINE(t):
                r'\n[\n 	]*'
                t.lexer.lineno += t.value.count("\n")
                if self.multilineScript:
                    t.value = "\n"
                else:
                    t = None
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

        if self.useCellToken:
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
            r'[a-zA-Z_\.][a-zA-Z_0-9\.]*'
            if t.value in self.logic_functions + self.fixed_implementations:
                t.type = t.value
            if t.value in ('TRUE', 'FALSE'):
                t.type = 'BOOLEAN'
            return t

        if not self.useCellToken:
            t_TEXT.__doc__ = r'[a-zA-Z_\.\[\]][a-zA-Z_0-9\.\[\]!]*'

        def t_error(t):
            print("Illegal character '%s'" % t.value[0])
            raise UntokenizableCodeException(t)
            #t.lexer.skip(1)

        t_ignore = " \t"

        lexer = lex.lex()

        return lexer

    def parser_error(self, place, step=""):
        raise Exception(f"Unknown {place}{': ' if len(step) > 0 else '' }{step}")

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
                        | lines NEWLINE
                        | NEWLINE lines
                        | NEWLINE lines NEWLINE
                '''

                if len(t) == 2:
                    t[0] = t[1]
                elif len(t) == 3 and subtokenIsType(t, 1, "NEWLINE"):
                    t[0] = t[2]
                elif len(t) == 3:
                    t[0] = t[1]
                elif len(t) == 4:
                    t[0] = t[2]
                else:
                    self.parser_error('start')

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
                        if type(t[1]) is ScriptNode:
                            t[0] = t[1]
                        else:
                            t[0] = ScriptNode(t[1])
                elif len(t) == 4:
                    if t[3] is None:
                        t[0] = t[1]
                    elif t[1] is None:
                        if type(t[3]) is ScriptNode:
                            t[0] = t[3]
                        else:
                            t[0] = ScriptNode(t[3])
                    else:
                        if type(t[3]) is ScriptNode:
                            t[0] = t[1]
                            for child in t[3].children:
                                t[0] = t[0].addChild(t[3].children[child])
                        else:
                            t[0] = t[1].addChild(t[3])
                else:
                    self.parser_error('Lines')

                return t[0]

            def p_line(t):
                '''line : COMMENT
                        | TICK
                        | OPEN
                        | CLOSE
                        | PRINT PRINT
                        | PRINT CELL_ADDRESS
                        | LOCK CELL_ADDRESS
                        | UNLOCK CELL_ADDRESS
                        | SETDEFAULTS CELL_ADDRESS
                        | CELL_ADDRESS LEFT_RIGHT_ASSIGN
                        | CELL_ADDRESS ASSIGN_VALUE
                        | INCLUDE_EXTERNAL_FILE TEXT
                        | PRINT EQUALS CELL_ADDRESS
                        | CELL_ADDRESS RIGHT_LEFT_ASSIGN statement
                        | TEXT ASSIGN_ALIAS CELL_ADDRESS
                        | RULE_INDICATOR TEXT LEFT_RIGHT_ASSIGN CELL_ADDRESS
                        | RULE_INDICATOR TEXT RIGHT_LEFT_ASSIGN CELL_ADDRESS
                        | RULE_INDICATOR TEXT LEFT_RIGHT_ASSIGN statement COMMA NUMBER COMMA NUMBER COMMA NUMBER
                        | RULE_INDICATOR TEXT RIGHT_LEFT_ASSIGN COMMA COMMA COMMA
                '''

                if len(t) == 2:

                    if subtokenIsType(t, 1, "TICK"):
                        t[0] = TickNode(len(t[1]))
                    elif subtokenIsType(t, 1, "OPEN"):
                        t[0] = OpenCloseFileNode(t[1], do_open=True)
                    elif subtokenIsType(t, 1, "CLOSE"):
                        t[0] = OpenCloseFileNode(t[1], do_open=False)
                    elif subtokenIsType(t, 1, "COMMENT"):
                        t[0] = None
                    else:
                        self.parser_error('Line', 'len-2')

                elif len(t) == 3:
                    if subtokenIsType(t,1,"SETDEFAULTS"):
                        t[0] = SetDefaultsNode(t[2])
                    elif subtokenIsType(t, 1, "PRINT"):
                        if subtokenIsType(t, 2, "PRINT"):
                            t[0] = PrintValueNode(print_all=True, print_value=True)
                        else:
                            t[0] = PrintValueNode(cell=t[2], print_value=True)
                    elif subtokenIsType(t, 2, "LEFT_RIGHT_ASSIGN"):
                        t[0] = AssignNode(t[1], EmptyValueNode())
                    elif subtokenIsType(t, 1, "LOCK"):
                        t[0] = LockAddressNode(t[2], lock=True)
                    elif subtokenIsType(t, 1, "UNLOCK"):
                        t[0] = LockAddressNode(t[2], lock=False)
                    elif subtokenIsType(t, 2, "ASSIGN_VALUE"):
                        t[0] = AssignNode(t[1], RawInputNode(t[2]))
                    elif subtokenIsType(t, 1, "INCLUDE_EXTERNAL_FILE"):
                        external_code = self.external_file_loader.load(t[2])
                        # Due to how ply works, we need a fresh lexer or it will throw out current tokens' pipeline
                        t[0] = self.parse(external_code, needs_fresh_lexer=True)
                        self.external_file_loader.unload(t[2])
                    else:
                        self.parser_error('Line', 'len-3')

                elif len(t) == 4:
                    if subtokenIsType(t, 2, "ASSIGN_ALIAS"):
                        if not self.useCellToken:
                            assert(address.match(t[1]) is None)
                            assert(address.match(t[3]) is not None)
                        t[0] = AliasNode(alias=t[1], cell=t[3])
                    elif subtokenIsType(t, 1, "PRINT"):
                        t[0] = PrintValueNode(cell=t[3], print_value=False)
                    elif subtokenIsType(t, 2, "RIGHT_LEFT_ASSIGN"):
                        t[0] = AssignNode(t[1], t[3])
                    else:
                        self.parser_error('Line', 'len-4')

                elif len(t) == 5:
                    assign_or_unassign = subtokenIsType(t, 3, "LEFT_RIGHT_ASSIGN")
                    t[0] = AssignAddressToRuleNode(t[2], t[4], assign = assign_or_unassign)

                elif len(t) == 7:
                    colors = (-1,-1,-1)
                    t[0] = AssignStatementToRuleNode(t[2], EmptyValueNode(), colors)

                elif len(t) == 11:
                    colors = (t[6], t[8], t[10])
                    t[0] = AssignStatementToRuleNode(t[2], t[4], colors)

                else:
                    self.parser_error('Line', 'Unknown length')

                return t[0]

            if not self.useCellToken:
                p_line.__doc__ = p_line.__doc__.replace("CELL_ADDRESS", "TEXT")

        # ~~~ END OF MULTILINE

        def p_statement(t):
            '''statement    : parameter
                            | callable_operation
                            | fixed_operation
            '''
            t[0] = t[1]
            return t[0]

        def p_statement_list(t):
            '''statement_list    : statement
                            | statement COMMA statement_list
            '''
            t[0] = [t[1]]
            if len(t) == 4:
                t[0] += t[3]
            return t[0]

        def p_callable_operation(t):
            '''callable_operation   : IF LPAREN statement COMMA  statement COMMA statement RPAREN
                                    | NOT LPAREN statement RPAREN
                                    | AND LPAREN statement COMMA statement RPAREN
                                    | OR LPAREN statement COMMA statement RPAREN
                                    | INDIRECT LPAREN statement RPAREN
                                    | TEXT LPAREN statement_list RPAREN'''
            if subtokenIsType(t, 1, "NOT"):
                t[0] = OperationNode(t[1], {0: t[3]})
            elif subtokenIsType(t, 1, "AND") or subtokenIsType(t, 1, "OR"):
                t[0] = OperationNode(t[1], {0: t[3], 1: t[5]})
            elif subtokenIsType(t, 1, "IF"):
                t[0] = IfNode(t[3], t[5], t[7])
            elif subtokenIsType(t, 1, "INDIRECT"):
                t[0] = IndirectNode(t[3])
            elif subtokenIsType(t, 1, "TEXT"):
                if t[1] not in self.spreadsheet_function_set.keys():
                    raise Exception("unknown text")
                else:
                    operands = self.spreadsheet_function_set[t[1]]
                    children = {k: v for k, v in enumerate(t[3])}
                    assert(len(children) == operands)
                    t[0] = OperationNode(t[1], children)
            else:
                self.parser_error('Operation')

            return t[0]


        def p_statement_parent(t):
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
            if subtokenIsType(t, 1, "MINUS"):
                t[0] = OperationNode("NEGATE", {0: t[2]})
            elif subtokenIsType(t, 2, "SMALLER") or subtokenIsType(t, 2, "BIGGER"):
                if subtokenIsType(t, 2, "SMALLER") and subtokenIsType(t, 3, "BIGGER"):  # <>
                    equals = OperationNode('EQUALS', {0: t[1], 1: t[4]})
                    t[0] = OperationNode('NOT', {0: equals})
                else:
                    second = t[4] if subtokenIsType(t, 3, "EQUALS") else t[3]
                    if subtokenIsType(t, 2, "BIGGER"):
                        bg, sm = (t[1], second)
                    else:
                        bg, sm = (second, t[1])  # IN CASE ITS SMALLER JUST REVERSE THE ORDER
                    bigger = OperationNode('BIGGER', {0: bg, 1: sm})
                    if subtokenIsType(t, 3, "EQUALS"):
                        equals = OperationNode('EQUALS', {0: bg, 1: sm})
                        t[0] = OperationNode('OR', {0: equals, 1: bigger})
                    else:
                        t[0] = bigger
            else:
                t[0] = OperationNode(getTokenType(t, 2), {0: t[1], 1: t[3]})

            return t[0]

        def p_parameter_int(t):
            '''parameter    : NUMBER'''
            t[0] = IntValueNode(t[1])
            return t[0]


        def p_parameter_STR(t):
            '''parameter    : STRING'''
            t[0] = StrValueNode(t[1])
            return t[0]

        def p_parameter_BOOL(t):
            '''parameter    : BOOLEAN'''
            t[0] = BoolValueNode(t[1])
            return t[0]

        def p_parameter_ADDRESS_OR_TEXT(t):
            '''parameter    : address'''
            t[0] = t[1]
            return t[0]

        def p_parameter_ADDRESS(t):
            '''address    : CELL_ADDRESS'''
            t[0] = ReferenceValueNode(t[1])
            return t[0]

        def p_parameter_TEXT(t):
            '''address  : TEXT'''
            if self.useCellToken:
                raise Exception(f"'{t[1]}' is Unknown")
            else:
                t[0] = ReferenceValueNode(t[1])
            return t[0]

        def p_error(t):
            print("Syntax error at '%s'" % t.value)
            raise UnparsableCodeException(t)

        parser = yacc.yacc(tabmodule="LexerParser_cachedParseTable", debug=False)

        return parser
