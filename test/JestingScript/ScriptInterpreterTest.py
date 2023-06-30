from JestingLang.Misc.JTesting.DereferencerHelper import DereferencerHelper
from unittest import TestCase
from JestingLang.LexerParser import LexerParser
from JestingLang.JestingScript.JDereferencer.ScriptDereferencer import (ScriptDereferencer, SDClosingUnopenedException,
                                                                        SDWritingUnopenedException, SDOpenFileException,
                                                                        SDCantResolveAliasException)
from JestingLang.JestingScript.JVisitors.ScriptInterpreterVisitor import ScriptInterpreterVisitor
from JestingLang.Misc.JTesting.NonFileExternalFileLoader import NonFileExternalFileLoader


test_loader = \
    NonFileExternalFileLoader(
        {
            "aliasA2": "TEST_NAME_ALIASED ? A2"
        }
    )


lexerParser = LexerParser(multilineScript=True, external_file_loader=test_loader)


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
        tree = lexerParser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(2, len(self.dereferencer.open_files))

    def test_file_exceptions(self):

        def _raise(_code, _exception):
            tree = lexerParser.parse(_code)
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
            "[test4]sheet1!A1 << 12" ])

        _raise(_code=code_write_error, _exception=SDWritingUnopenedException)

        code_no_errors = '\n'.join([
            "} test5",
            "[test5]sheet1!A1 << 12",
            "{ test5"])

        tree_no_errors = lexerParser.parse(code_no_errors)
        self.visitor.visit(tree_no_errors)

    def test_single_write(self):

        code = '\n'.join([
            "} test1",
            "[test1]sheet1!A1 << 12",
            "{ test1"])

        tree= lexerParser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(0, len(self.dereferencer.open_files))
        self.assertEqual(12, self.cache['[test1]']['sheet1!']['A1'].value)

    def test_different_writes(self):

        code = '\n'.join([
            "} test1",
            "[test1]sheet1!A1 <<    12",
            "[test1]sheet1!A2 << test",
            "[test1]sheet1!A3 <~ 12+1",
            "[test1]sheet1!A4 << = 12+1",
            "[test1]sheet1!A5 <~ \"13\"",
            "{ test1"])

        tree= lexerParser.parse(code)
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
            "[test1]sheet1!A1 << 12",
            ";",
            "[test1]sheet1!A2 <~ [test1]sheet1!A1+2",
            "// WITHOUT PING",
            "[test1]sheet1!A1 << 12",
            "[test1]sheet1!A3 << 3",
            "[test1]sheet1!A4 <~ A3 + 1",
            "{ test1"])

        tree= lexerParser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(12, self.cache['[test1]']['sheet1!']['A1'].value)
        self.assertEqual(14, self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(3, self.cache['[test1]']['sheet1!']['A3'].value)
        self.assertEqual(1, self.cache['[test1]']['sheet1!']['A4'].value)

    def test_self_ref_and_slow_visitor(self):
        code = '\n'.join([
                "} test1",
                "// WITH PING",
                "[test1]sheet1!A1 <~ A1+1",
                ";",
                "[test1]sheet1!A2 <~ A2+1",
                ";",
                "[test1]sheet1!A3 <~ A3+1",
                ";",
                "[test1]sheet1!A4 <~ A4+1",
                ";",
                "[test1]sheet1!A5 <~ A5+1",
                "{ test1"])

        tree = lexerParser.parse(code)

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
                "[test1]sheet1!A1 <~ A1 + A2 + 1",
                "[test1]sheet1!A2 << 3",
                ";",
                "[test1]sheet1!A3 <~ A1 + A2 + 1",
                "{ test1"
                ""])

        tree = lexerParser.parse(code)

        self.slow_visitor.visit(tree)
        self.assertEqual(4, self.cache['[test1]']['sheet1!']['A1'].value)
        self.assertEqual(3, self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(None, self.cache['[test1]']['sheet1!']['A3'].value)

    def test_aliases_with_error(self):
        code = '\n'.join([
                "} test1",
                "SARASA ? A1",
                "{ test1",
                " "])

        tree = lexerParser.parse(code)

        with self.assertRaises(SDCantResolveAliasException):
            self.slow_visitor.visit(tree)

    def test_aliases(self):
        code = '\n'.join([
            "} test1",
            "@ [test1]sheet1!A1",
            "",
            "TEST_NAME ? A2",
            "TEST_NAME << 2",
            "",
            "TEST_NAME ? A3",
            "TEST_NAME << 3",
            "A4 <~ TEST_NAME + 1 ",
            ";",
            ";",
            "{ test1",
            " "])

        tree = lexerParser.parse(code)
        self.slow_visitor.visit(tree)

        self.assertEqual(2, self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(3, self.cache['[test1]']['sheet1!']['A3'].value)
        self.assertEqual(4, self.cache['[test1]']['sheet1!']['A4'].value)

        manager = self.slow_visitor.scriptManager
        self.assertTrue('TEST_NAME' in manager.aliases.keys())
        self.assertTrue((None, '[test1]', 'sheet1!', 'A2', None) in manager.reverse_aliases.keys())

    def test_alias_and_include(self):
        code = '\n'.join([
            "} test1",
            "@ [test1]sheet1!A1",
            "*INCLUDE* aliasA2",
            "TEST_NAME_ALIASED << 10",
            "A3 <~ TEST_NAME_ALIASED + 1 ",
            ";",
            "{ test1",
            " "])

        tree = lexerParser.parse(code)
        self.slow_visitor.visit(tree)

        self.assertEqual(10, self.cache['[test1]']['sheet1!']['A2'].value)
        self.assertEqual(11, self.cache['[test1]']['sheet1!']['A3'].value)

        manager = self.slow_visitor.scriptManager
        self.assertTrue('TEST_NAME_ALIASED' in manager.aliases.keys())
        self.assertTrue((None, '[test1]', 'sheet1!', 'A2', None) in manager.reverse_aliases.keys())

    def test_color_basic(self):
        code = '\n'.join([
            "} test1",
            "@ [test1]sheet1!A1",
            "# RULE1 ~> 1=1 , 2 , 3 , 1",
            "# RULE2 ~> 2=3 , 1 , 0 , 2",
            "# RULE3 ~> 1=3 , 9 , 1 , 0",
            "# RULE1 ~> A3 ",
            "# RULE1 ~> A4 ",
            "# RULE1 ~> A5 ",
            "# RULE2 ~> A6 ",
            "# RULE2 ~> A7 ",
            "# RULE3 ~> A9 ",
            "# RULE2 <~ ,,,",
            "# RULE1 <~ A4",
            "{ test1"
        ])
        tree = lexerParser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(2, len(self.dereferencer.rules))
        #Rule 1
        self.assertEqual(tuple,type(self.dereferencer.rules["RULE1"]))
        self.assertEquals((2, 3, 1), self.dereferencer.rules["RULE1"][0][1])
        self.assertEqual(2,len(self.dereferencer.rules["RULE1"][1]))
        self.assertTrue("A3" in self.dereferencer.rules["RULE1"][1])
        self.assertTrue("A5" in self.dereferencer.rules["RULE1"][1])
        #Rule 3
        self.assertEqual(tuple,type(self.dereferencer.rules["RULE3"]))
        self.assertEquals((9, 1, 0), self.dereferencer.rules["RULE3"][0][1])
        self.assertEqual(1,len(self.dereferencer.rules["RULE3"][1]))
        self.assertTrue("A9" in self.dereferencer.rules["RULE3"][1])


    def test_lock_basic(self):
        code = '\n'.join([
            "} test1",
            "(+) A2",
            "(+) A3",
            "(+) A4",
            "(+) A5",
            "(+) A6",
            "(-) A5",
            "(-) A4",
            "{ test1"
        ])

        tree = lexerParser.parse(code)
        self.visitor.visit(tree)
        self.assertEqual(3, len(self.dereferencer.locked_addresses))
        self.assertTrue("A2" in self.dereferencer.locked_addresses)
        self.assertTrue("A3" in self.dereferencer.locked_addresses)
        self.assertTrue("A6" in self.dereferencer.locked_addresses)

if __name__ == "__main__":
    print(40)