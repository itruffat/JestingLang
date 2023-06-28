from JestingLang.Misc.JTesting.DereferencerHelper import DereferencerHelper
from unittest import TestCase
from JestingLang.LexerParser import LexerParser
from JestingLang.JestingScript.JDereferencer.ScriptDereferencer import (ScriptDereferencer, SDClosingUnopenedException,
                                                                        SDWritingUnopenedException, SDOpenFileException)
from JestingLang.JestingScript.JVisitors.ScriptInterpreterVisitor import ScriptInterpreterVisitor

lexerParser = LexerParser(multilineScript=True)
parser = lexerParser.parser


class ScriptInterpreterTest(TestCase):

    def setUp(self) -> None:
        self.memory = {}
        self.cache = {}
        self.dereferencer = ScriptDereferencer(memory=self.memory, cache=self.cache)
        self.helper = DereferencerHelper(self.dereferencer)
        self.visitor = ScriptInterpreterVisitor(self.dereferencer, resolveVolatile=True)
        self.slow_visitor = ScriptInterpreterVisitor(self.dereferencer, resolveVolatile=True, insertionUpdate=False)

    def tearDown(self):
        del self.memory
        del self.dereferencer
        del self.helper
        del self.visitor

    def test_open(self):
        self.helper.writeNumber("A1", 14)
        code = '\n'.join([
            "} sarasa",
            "} pepe"
        ])
        tree = parser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(2, len(self.dereferencer.open_files))

    def test_file_exceptions(self):

        def _raise(_code, _exception):
            tree = parser.parse(_code)
            with self.assertRaises(_exception):
                self.visitor.visit(tree)

        code_open_error = '\n'.join([
            "} test1",
            "} test1" ])

        _raise(_code=code_open_error, _exception=SDOpenFileException)

        code_close_error = '\n'.join([
            "} test2",
            "{ test2UNKNOWN" ])

        _raise(_code=code_close_error, _exception=SDClosingUnopenedException)

        code_write_error = '\n'.join([
            "} test3",
            "[test4]sheet1!A1 @ 12" ])

        _raise(_code=code_write_error, _exception=SDWritingUnopenedException)

        code_no_errors = '\n'.join([
            "} test5",
            "[test5]sheet1!A1 @ 12",
            "{ test5"])

        tree_no_errors = parser.parse(code_no_errors)
        self.visitor.visit(tree_no_errors)

    def test_single_write(self):

        code = '\n'.join([
            "} test1",
            "[test1]sheet1!A1 @ 12",
            "{ test1"])

        tree= parser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(0, len(self.dereferencer.open_files))
        self.assertEqual(12, self.cache['[test1]']['sheet1!']['A1'].value)

    def test_different_writes(self):

        code = '\n'.join([
            "} test1",
            "[test1]sheet1!A1 @    12",
            "[test1]sheet1!A2 @ test",
            "[test1]sheet1!A3 @= 12+1",
            "[test1]sheet1!A4 @ = 12+1",
            "[test1]sheet1!A5 @= \"13\"",
            "{ test1"])

        tree= parser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(12, self.cache['[test1]']['sheet1!']['A1'].value)
        self.assertEqual("test", self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(13, self.cache['[test1]']['sheet1!']['A3'].value)
        self.assertEqual("= 12+1", self.cache['[test1]']['sheet1!']['A4'].value)
        self.assertEqual("13", self.cache['[test1]']['sheet1!']['A5'].value)

    def test_ref(self):

        code = '\n'.join([
            "} test1",
            "// WITH PING",
            "[test1]sheet1!A1 @ 12",
            "~",
            "[test1]sheet1!A2 @= [test1]sheet1!A1+2",
            "// WITHOUT PING",
            "[test1]sheet1!A1 @ 12",
            "[test1]sheet1!A3 @ 3",
            "[test1]sheet1!A4 @= A3 + 1",
            "{ test1"])

        tree= parser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(12, self.cache['[test1]']['sheet1!']['A1'].value)
        self.assertEqual(14, self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(3, self.cache['[test1]']['sheet1!']['A3'].value)
        self.assertEqual(1, self.cache['[test1]']['sheet1!']['A4'].value)

    def test_self_ref_and_slow_visitor(self):
        code = '\n'.join([
                "} test1",
                "// WITH PING",
                "[test1]sheet1!A1 @= A1+1",
                "~",
                "[test1]sheet1!A2 @= A2+1",
                "~",
                "[test1]sheet1!A3 @= A3+1",
                "~",
                "[test1]sheet1!A4 @= A4+1",
                "~",
                "[test1]sheet1!A5 @= A5+1",
                "{ test1"])

        tree = parser.parse(code)

        self.slow_visitor.visit(tree)
        self.assertEqual(4, self.cache['[test1]']['sheet1!']['A1'].value)
        self.assertEqual(3, self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(2, self.cache['[test1]']['sheet1!']['A3'].value)
        self.assertEqual(1, self.cache['[test1]']['sheet1!']['A4'].value)
        self.assertEqual(None, self.cache['[test1]']['sheet1!']['A5'].value)

        self.tearDown()
        self.setUp()

        self.visitor.visit(tree)
        self.assertEqual(5, self.cache['[test1]']['sheet1!']['A1'].value)
        self.assertEqual(4, self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(3, self.cache['[test1]']['sheet1!']['A3'].value)
        self.assertEqual(2, self.cache['[test1]']['sheet1!']['A4'].value)
        self.assertEqual(1, self.cache['[test1]']['sheet1!']['A5'].value)

    def test_tick_and_rawvalue(self):
        code = '\n'.join([
                "} test1",
                "// WITH PING",
                "[test1]sheet1!A1 @= A1 + A2 + 1",
                "[test1]sheet1!A2 @ 3",
                "~",
                "[test1]sheet1!A3 @= A1 + A2 + 1",
                "{ test1"
                ""])

        tree = parser.parse(code)

        self.slow_visitor.visit(tree)
        self.assertEqual(4, self.cache['[test1]']['sheet1!']['A1'].value)
        self.assertEqual(3, self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(None, self.cache['[test1]']['sheet1!']['A3'].value)

if __name__ == "__main__":
    print(40)