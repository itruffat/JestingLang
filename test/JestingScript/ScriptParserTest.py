from JestingLang.LexerParser import LexerParser
from unittest import TestCase
from JestingLang.Misc.JTesting.NonFileExternalFileLoader import NonFileExternalFileLoader
from JestingLang.JestingScript.JFileLoader.ExternalFileLoader import ExternalLoaderException

a1_code = "A3 @=A1+12 \nA2 @ 1+1"
cyclical_error_code = "#INCLUDE fileCyclicalError \n A3 @=A1+12 \nA2 @ 1+1"

test_loader = \
    NonFileExternalFileLoader(
        {"fileA1": a1_code,
         "fileCyclicalError": cyclical_error_code
         }
    )

parser = LexerParser(multilineScript=True, external_file_loader=test_loader).parser

class ScriptParserTest(TestCase):

    def test_include(self):
        answer = parser.parse("#INCLUDE fileA1")
        expected = parser.parse(a1_code)
        self.assertEqual(type(answer), type(expected))
        self.assertEqual(len(answer.children), len(expected.children))
        for n in range(len(answer.children)):
            answer_n = answer.children[n]
            expected_n = expected.children[n]
            self.assertEqual(type(answer_n), type(expected_n))

    def test_include_cyclical_fails(self):
        with self.assertRaises(ExternalLoaderException) as external_exception:
            parser.parse(cyclical_error_code)
        self.assertTrue(external_exception.exception.on_open)

