import JestingLang.JParsing.LexerParser
from unittest import TestCase

lexer = JestingLang.JParsing.LexerParser.lexer

def unmap_token(token):
    return (token.type, token.value, token.lineno, token.lexpos)

def squeeze_lexer(_input, _lexer=lexer):
    _lexer.input(_input)
    return [unmap_token(token) for token in _lexer]


class lexerTest(TestCase):

    def test_text(self):
        expected_t = ("TEXT", "A", 1, 0)
        new_t = squeeze_lexer("A")[0]
        self.assertEqual(expected_t,new_t)

    def test_number(self):
        expected_t = ("NUMBER", 12, 1, 0)
        new_t = squeeze_lexer("12")[0]
        self.assertEqual(expected_t,new_t)

    def test_plus(self):
        expected_ts = [("TEXT", "A", 1, 0), ('PLUS', '+', 1, 1), ("NUMBER", 12, 1, 2)]
        new_ts = squeeze_lexer("A+12")
        self.assertEqual(expected_ts,new_ts)
