from JestingLang.LexerParser import LexerParser
from unittest import TestCase
from JestingLang.Misc.JTesting.LexerParserHelpers import helper_lexer_pointer, squeeze_lexer

class LexerTest(TestCase):

    def setUp(self) -> None:
        self.lexer = LexerParser(multilineScript=False).lexer
        helper_lexer_pointer.append(self.lexer)

    def tearDown(self):
        helper_lexer_pointer.pop()
        del self.lexer

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
        self.assertEqual(expected_ts, new_ts)

    def test_minus(self):
        expected_ts = [("TEXT", "A", 1, 0), ('MINUS', '-', 1, 1), ("NUMBER", 12, 1, 2)]
        new_ts = squeeze_lexer("A-12")
        self.assertEqual(expected_ts, new_ts)
