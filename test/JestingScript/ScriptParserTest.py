from JestingLang.LexerParser import LexerParser
from unittest import TestCase
from JestingLang.Misc.JTesting.NonFileExternalFileLoader import NonFileExternalFileLoader
from JestingLang.JestingScript.JFileLoader.ExternalFileLoader import ExternalLoaderException

a1_code = "A3 @=A1+12 \nA2 @ 1+1"
cyclical_error_code = f"#INCLUDE fileCyclicalError \n {a1_code}"

test_loader = \
    NonFileExternalFileLoader(
        {
            "fileA1": a1_code,
            "fileCyclicalError": cyclical_error_code,
        }
    )

lexerParser = LexerParser(multilineScript=True, external_file_loader=test_loader)
parser = lexerParser.parser


class ScriptParserTest(TestCase):

    def test_include(self):
        answer = parser.parse("#INCLUDE fileA1")
        expected = parser.parse(a1_code)
        self.assertEqual(type(expected), type(answer))
        self.assertEqual(len(expected.children), len(answer.children))
        for n in range(len(answer.children)):
            answer_n = answer.children[n]
            expected_n = expected.children[n]
            self.assertEqual(type(expected_n), type(answer_n))

    def test_include_with_lines_before_and_after(self):
        new_line ="C1 @ 2"
        answer = parser.parse(new_line + "\n" + "#INCLUDE fileA1" + "\n" + new_line)
        expected = parser.parse(new_line + "\n" + a1_code + "\n" + new_line)
        self.assertEqual(type(expected), type(answer))
        self.assertEqual(len(expected.children), len(answer.children))
        for n in range(len(answer.children)):
            answer_n = answer.children[n]
            expected_n = expected.children[n]
            self.assertEqual(type(expected_n), type(answer_n))
            self.assertEqual(expected_n.target, answer_n.target)

    def test_include_cyclical_fails(self):
        with self.assertRaises(ExternalLoaderException) as external_exception:
            parser.parse(cyclical_error_code)
        self.assertTrue(external_exception.exception.on_open)

    def test_assign_alias(self):

        with self.assertRaises(AssertionError):
            parser.parse("B1 ? A1")  # Assigning to a Cell

        with self.assertRaises(AssertionError):
            parser.parse("TEST3 ? TEST4")  # Assigning something that's not a cell

        with self.assertRaises(AssertionError):
            parser.parse("TEST1 ? A1\n TEST2 ? TEST1")  # Assigning something that's a cell-reference (not a cell)

        parser.parse("TEST1 ? A1")
        parser.parse("TEST1 ? A2\n TEST2 ? A3")
