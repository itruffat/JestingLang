import JestingLang.JParsing.LexerParser
from JestingLang.JParsing.JestingAST import *
from unittest import TestCase

parser = JestingLang.JParsing.LexerParser.parser


class parserTest(TestCase):

    def test_reference(self):
        answer = parser.parse("A1")
        expected = ReferenceValueNode("A1")
        self.assertEqual(type(answer), type(expected))
        self.assertEqual(answer.value, expected.value)