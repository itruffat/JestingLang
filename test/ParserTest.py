from JestingLang.LexerParser import LexerParser
from JestingLang.Core.JParsing.JestingAST import ReferenceValueNode
from unittest import TestCase

parser = LexerParser().parser


class ParserTest(TestCase):

    def test_reference(self):
        answer = parser.parse("A1")
        expected = ReferenceValueNode("A1")
        self.assertEqual(type(answer), type(expected))
        self.assertEqual(answer.value, expected.value)