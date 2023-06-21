from JestingLang.Misc.JTesting.DereferencerHelper import DereferencerHelper
from JestingLang.LexerParser import LexerParser
from JestingLang.JestingScript.JDereferencer.ScriptDereferencer import (ScriptDereferencer, SDClosingUnopenedException,
                                                                        SDWritingUnopenedException, SDOpenFileException)
from JestingLang.JestingScript.JVisitors.ScriptInterpreterVisitor import ScriptInterpreterVisitor

lexerParser = LexerParser(multilineScript=True)
parser = lexerParser.parser


class ScriptInterpreterTest():

    def setUp(self) -> None:
        self.memory = {}
        self.cache = {}
        self.dereferencer = ScriptDereferencer(memory=self.memory, cache=self.cache)
        self.helper = DereferencerHelper(self.dereferencer)
        self.visitor = ScriptInterpreterVisitor(self.dereferencer, resolveVolatile=True)

    def tearDown(self):
        del self.memory
        del self.dereferencer
        del self.helper
        del self.visitor

    def est_open(self):
        self.helper.writeNumber("A1", 14)
        code = '\n'.join([
            "} sarasa",
            "} pepe"
        ])
        tree = parser.parse(code)
        self.visitor.visit(tree)

    def est_file_exceptions(self):

        def _raise(_code, _exception):
            tree = parser.parse(_code)

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

    def est_single_write(self):

        code = '\n'.join([
            "} test1",
            "[test1]sheet1!A1 @ 12",
            "{ test1"])

        tree= parser.parse(code)
        self.visitor.visit(tree)

    def est_different_writes(self):

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

    def est_ref(self):

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

    def est_self_ref(self):
        code = '\n'.join([
            "} test1",
            "// WITH PING",
            "[test1]sheet1!A1 @= A1+1",
            "~",
            "~",
            "~",
            "~",
            "![test1]sheet1!A1",
            "!=[test1]sheet1!A1",
            "{ test1"])

        tree= parser.parse(code)
        self.visitor.visit(tree)

if __name__ == "__main__":
    a = ScriptInterpreterTest()
    a.setUp()
    a.est_self_ref()
