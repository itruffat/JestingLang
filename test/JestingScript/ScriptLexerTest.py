from JestingLang.LexerParser import LexerParser
from unittest import TestCase
from JestingLang.Misc.JTesting.LexerParserHelpers import helper_lexer_pointer, squeeze_lexer

class MultilineLexerTest(TestCase):

    def setUp(self) -> None:
        self.lexer = LexerParser(multilineScript=True).lexer
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

    def test_assign_with_value(self):
        expected_ts = [('CELL_ADDRESS', 'Asheet1!A3', 1, 0), ('ASSIGN_VALUE', '=12 + 1', 1, 11)]
        new_ts = squeeze_lexer("Asheet1!A3 @ =12 + 1")
        self.assertEqual(expected_ts, new_ts)

    def test_assign_with_statement(self):
        expected_ts = [
            ('CELL_ADDRESS', 'Asheet1!A3', 1, 0), ('ASSIGN_FORMULA', '@=', 1, 11),
            ('NUMBER', 12, 1, 14), ('PLUS', '+', 1, 17), ('NUMBER', 1, 1, 19)]
        new_ts = squeeze_lexer("Asheet1!A3 @= 12 + 1")
        self.assertEqual(expected_ts, new_ts)

    def test_lines(self):
        expected_ts = [
            ('COMMENT', 'THIS IS A COMMENT', 1, 0),
             ('NEWLINE', '\n', 1, 19),
             ('PRINT', '!', 2, 20),
             ('CELL_ADDRESS', 'a1', 2, 22),
             ('NEWLINE', '\n', 2, 24),
             ('PRINT', '!', 3, 26),
             ('PRINT', '!', 3, 27),
             ('NEWLINE', '\n', 3, 28),
             ('TICK', '~', 4, 29),
             ('NEWLINE', '\n', 4, 30),
             ('TICK', '~~~~', 5, 31),
             ('NEWLINE', '\n', 5, 35),
             ('OPEN', '[test1]', 6, 36),
             ('NEWLINE', '\n', 6, 44),
             ('CLOSE', '[test2]', 7, 45),
             ('NEWLINE', '\n', 7, 53),
             ('SETDEFAULTS', ':', 8, 55),
             ('CELL_ADDRESS', 'a1', 8, 57),
             ('NEWLINE', '\n', 8, 60),
             ('CELL_ADDRESS', 'A1', 9, 62),
             ('UNASSIGN', '@', 9, 65),
             ('NEWLINE', '\n', 9, 66)]
        new_ts = squeeze_lexer("//THIS IS A COMMENT\n! a1\n !!\n~\n~~~~\n} test1 \n{ test2 \n : a1 \n A1 @\n")
        self.assertEqual(expected_ts, new_ts)

    def test_include(self):
        expected_ts = [('INCLUDE_EXTERNAL_FILE', '#INCLUDE', 1, 0), ('TEXT', '_test.xml', 1, 9)]
        new_ts = squeeze_lexer("#INCLUDE _test.xml")
        self.assertEqual(expected_ts, new_ts)


    def test_assign(self):
        expected_ts = [('TEXT', 'TEST1', 1, 0), ('ASSIGN_ALIAS', '?', 1, 6), ('TEXT', 'A1', 1, 8)]
        new_ts = squeeze_lexer("TEST1 ? A1")
        self.assertEqual(expected_ts, new_ts)

