from JestingLang.LexerParser import LexerParser
from JestingLang.Core.JVisitors.ReferencesListerVisitor import ReferencesListerVisitor
from unittest import TestCase

lexerParser = LexerParser()
parser = lexerParser.parser
visitor = ReferencesListerVisitor()

class ReferencesListerTest(TestCase):

    def test_simple_case(self):
        tree = parser.parse("A1")
        answer = visitor.visit(tree)
        self.assertEqual(["A1"], answer)

    def test_operations(self):
        tree = parser.parse("A1+A2-(A3*A5)/A6")
        answer = visitor.visit(tree)
        self.assertEqual(["A1","A2","A3","A5","A6"], answer)

    def test_indirect(self):
        tree = parser.parse("INDIRECT(A3+1)")
        answer = visitor.visit(tree)
        self.assertEqual([], answer)

    def test_if(self):
        tree = parser.parse("IF( A3+1, INDIRECT(A4), A1 & A2 )")
        answer = visitor.visit(tree)
        self.assertEqual(["A3", "A1", "A2"], answer)