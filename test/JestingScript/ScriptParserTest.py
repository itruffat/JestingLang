from JestingLang.Core.JParsing.JestingAST import OperationNode, ReferenceValueNode, EmptyValueNode
from JestingLang.JestingScript.JParsing.JestingScriptAST import ScriptNode, AssignStatementToRuleNode
from JestingLang.LexerParser import LexerParser, UnparsableCodeException, UntokenizableCodeException
from unittest import TestCase
from JestingLang.Misc.JTesting.NonFileExternalFileLoader import NonFileExternalFileLoader
from JestingLang.JestingScript.JFileLoader.ExternalFileLoader import ExternalLoaderException

a1_code = "A3 <~ A1+12 \nA2 << 1+1"
cyclical_error_code = f"*INCLUDE* fileCyclicalError \n {a1_code}"

test_loader = \
    NonFileExternalFileLoader(
        {
            "fileA1": a1_code,
            "fileCyclicalError": cyclical_error_code,
        }
    )

lexerParser = LexerParser(multilineScript=True, external_file_loader=test_loader)


class ScriptParserTest(TestCase):

    def test_errors(self):
        # No errors
        code0 = "A1 << 2 \n } TEST1 \n TEST3 ? A1"
        lexerParser.lexer.input(code0)
        lexerParser.parse(code0)

        # Token error
        code1 = "A1 $ << 2 \n } TEST1 \n TEST3 ? A1"
        with self.assertRaises(UntokenizableCodeException):
            lexerParser.parse(code1)

        # Parse error
        code2 = "A1 << 2 \n } TEST1 TEST3 ? A1"
        with self.assertRaises(UnparsableCodeException):
            lexerParser.parse(code2)


    def test_include(self):
        answer = lexerParser.parse("*INCLUDE* fileA1")
        expected = lexerParser.parse(a1_code)
        self.assertEqual(type(expected), type(answer))
        self.assertEqual(len(expected.children), len(answer.children))
        for n in range(len(answer.children)):
            answer_n = answer.children[n]
            expected_n = expected.children[n]
            self.assertEqual(type(expected_n), type(answer_n))

    def test_color_rule_define(self):
        answer = lexerParser.parse("# RULE1 ~> 1=1 , 12 , 11 , 10 ")
        self.assertEqual(ScriptNode, type(answer))
        self.assertEqual(1, len(answer.children) )
        self.assertEqual("RULE1", answer.children[0].source)
        self.assertEqual(AssignStatementToRuleNode, type(answer.children[0]))
        self.assertEqual(1, len(answer.children[0].children))
        self.assertEqual(OperationNode, type(answer.children[0].children[0]))
        self.assertEqual((12, 11, 10), answer.children[0].color)


    def test_color_rule_delete(self):
        answer2 = lexerParser.parse("# RULE1 <~ , , , ")
        self.assertEqual(ScriptNode, type(answer2))
        self.assertEqual(1, len(answer2.children))
        self.assertEqual("RULE1", answer2.children[0].source)
        self.assertEqual(AssignStatementToRuleNode, type(answer2.children[0]))
        self.assertEqual(1, len(answer2.children[0].children))
        self.assertEqual(EmptyValueNode, type(answer2.children[0].children[0]))

    def test_color_rule_apply(self):
        answer = lexerParser.parse("# RULE1 ~> A1 ")
        self.assertEqual(ScriptNode, type(answer))
        self.assertEqual(1, len(answer.children))
        self.assertEqual("RULE1", answer.children[0].source)
        self.assertEqual("A1", answer.children[0].target)
        self.assertEqual(True, answer.children[0].assign)


    def test_color_rule_remove(self):
        answer2 = lexerParser.parse("# RULE1 <~ A1 ")
        self.assertEqual(ScriptNode, type(answer2))
        self.assertEqual(1, len(answer2.children))
        self.assertEqual("RULE1", answer2.children[0].source)
        self.assertEqual("A1", answer2.children[0].target)
        self.assertEqual(False, answer2.children[0].assign)

    def test_include_with_lines_before_and_after(self):
        new_line ="C1 << 2"
        answer = lexerParser.parse(new_line + "\n" + "*INCLUDE* fileA1" + "\n" + new_line)
        expected = lexerParser.parse(new_line + "\n" + a1_code + "\n" + new_line)
        self.assertEqual(type(expected), type(answer))
        self.assertEqual(len(expected.children), len(answer.children))
        for n in range(len(answer.children)):
            answer_n = answer.children[n]
            expected_n = expected.children[n]
            self.assertEqual(type(expected_n), type(answer_n))
            self.assertEqual(expected_n.target, answer_n.target)

    def test_include_cyclical_fails(self):
        with self.assertRaises(ExternalLoaderException) as external_exception:
            lexerParser.parse(cyclical_error_code)
        self.assertTrue(external_exception.exception.on_open)

    def test_assign_alias(self):

        with self.assertRaises(AssertionError):
            lexerParser.parse("B1 ? A1")  # Assigning to a Cell

        with self.assertRaises(AssertionError):
            lexerParser.parse("TEST3 ? TEST4")  # Assigning something that's not a cell

        with self.assertRaises(AssertionError):
            lexerParser.parse("TEST1 ? A1\n TEST2 ? TEST1")  # Assigning something that's a cell-reference (not a cell)

        lexerParser.parse("TEST1 ? A1")
        lexerParser.parse("TEST1 ? A2\n TEST2 ? A3")
