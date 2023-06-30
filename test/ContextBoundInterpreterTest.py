from JestingLang.Core.JVisitors.ContextBoundInterpreterVisitor import ContextBoundInterpreterVisitor
from JestingLang.Core.JDereferencer.KeyValueDereferencer import KeyValueDereferencer
from JestingLang.Core.JDereferencer.CachedDereferencer import CachedDereferencer
from JestingLang.Misc.JTesting.DereferencerHelper import DereferencerHelper
from unittest import TestCase
from JestingLang.LexerParser import LexerParser

lexerParser = LexerParser()


class ContextBoundInterpreterWithKeyValueDereferencerTest(TestCase):

    def setUp(self) -> None:
        self.dereferencer = KeyValueDereferencer()
        self.visitor_fixed = \
            ContextBoundInterpreterVisitor(self.dereferencer, resolveVolatile=False)
        self.visitor_volatile = \
            ContextBoundInterpreterVisitor(self.dereferencer, resolveVolatile=True)
        self.helper = DereferencerHelper(self.dereferencer, writes_cache=False)

    def tearDown(self):
        del self.visitor_fixed
        del self.visitor_volatile
        del self.helper
        del self.dereferencer

    def test_ampersand(self):
        tree = lexerParser.parse("\"A\" & 1")
        self.assertEqual("A1", self.visitor_fixed.visit(tree).value)

    def test_visit_node(self):
        self.helper.writeNumber("A1", 12)
        tree = lexerParser.parse("A1")
        self.assertEqual("A1", self.visitor_fixed.visit(tree).value)
        self.assertEqual(12, self.visitor_volatile.visit(tree).value)

    def test_indirect_visit_node(self):
        self.helper.writeNumber("A1", 16)
        tree = lexerParser.parse("INDIRECT(\"A\" & 1)")
        self.assertEqual("IndirectNode", self.visitor_fixed.visit(tree).__class__.__name__)
        self.assertEqual("A1", self.visitor_fixed.visit(tree).children[0].value)
        self.assertEqual(16, self.visitor_volatile.visit(tree).value)

    def test_sum_of_visit(self):
        self.helper.writeNumber("A1", 11)
        self.helper.writeNumber("A2", 19)
        tree = lexerParser.parse("A1+A2")
        self.assertEqual("OperationNode", self.visitor_fixed.visit(tree).__class__.__name__)
        self.assertEqual("PLUS", self.visitor_fixed.visit(tree).operation)
        self.assertEqual("A1",self.visitor_fixed.visit(tree).children[0].value)
        self.assertEqual("A2",self.visitor_fixed.visit(tree).children[1].value)
        self.assertEqual(30, self.visitor_volatile.visit(tree).value)

    def test_modulo_of_visit(self):
        self.helper.writeNumber("A1", 10)
        self.helper.writeNumber("A2", 6)
        self.helper.writeNumber("A3", 4)
        self.helper.writeNumber("A4", 3)
        self.helper.writeNumber("A5", 2)
        #A2
        tree = lexerParser.parse("MOD(A1,A2)")
        self.assertEqual("OperationNode", self.visitor_fixed.visit(tree).__class__.__name__)
        self.assertEqual("MOD", self.visitor_fixed.visit(tree).operation)
        self.assertEqual(4, self.visitor_volatile.visit(tree).value)
        #A3
        tree = lexerParser.parse("MOD(A1,A3)")
        self.assertEqual("OperationNode", self.visitor_fixed.visit(tree).__class__.__name__)
        self.assertEqual("MOD", self.visitor_fixed.visit(tree).operation)
        self.assertEqual(2, self.visitor_volatile.visit(tree).value)
        #A4
        tree = lexerParser.parse("MOD(A1,A4)")
        self.assertEqual("OperationNode", self.visitor_fixed.visit(tree).__class__.__name__)
        self.assertEqual("MOD", self.visitor_fixed.visit(tree).operation)
        self.assertEqual(1, self.visitor_volatile.visit(tree).value)
        #A5
        tree = lexerParser.parse("MOD(A1,A5)")
        self.assertEqual("OperationNode", self.visitor_fixed.visit(tree).__class__.__name__)
        self.assertEqual("MOD", self.visitor_fixed.visit(tree).operation)
        self.assertEqual(0, self.visitor_volatile.visit(tree).value)
        #INT
        tree = lexerParser.parse("MOD(A1,9)")
        self.assertEqual("OperationNode", self.visitor_fixed.visit(tree).__class__.__name__)
        self.assertEqual("MOD", self.visitor_fixed.visit(tree).operation)
        self.assertEqual(1, self.visitor_volatile.visit(tree).value)


    def test_sum_of_visit_with_ref(self):
        self.helper.writeNumber("A1", 14)
        tree = lexerParser.parse("A1*2")
        self.dereferencer.write("A2", tree)
        tree2 = lexerParser.parse("1 + A2 + A1")
        self.assertEqual(43, self.visitor_volatile.visit(tree2).value)

    def test_sum_of_visit_with_ref_and_changes(self):
        self.helper.writeNumber("A1", 12)
        self.dereferencer.write("A2", lexerParser.parse("A1*2"))
        self.assertEqual(37, self.visitor_volatile.visit(lexerParser.parse("1 + A2 + A1")).value)
        self.helper.writeNumber("A1", 10)
        self.assertEqual(31, self.visitor_volatile.visit(lexerParser.parse("1 + A2 + A1")).value)

    def test_double_indirection(self):
        self.helper.writeNumber("A1", 12)
        self.dereferencer.write("A2", lexerParser.parse("A1"))
        self.dereferencer.write("A3", lexerParser.parse("A2"))
        self.assertEqual(12, self.visitor_volatile.visit(lexerParser.parse("A3")).value)
        self.helper.writeNumber("A1", 10)
        self.assertEqual(10, self.visitor_volatile.visit(lexerParser.parse("A3")).value)

    def test_cycle(self):
        self.dereferencer.write("A1", lexerParser.parse("A1"))
        self.assertEquals("A1", self.visitor_fixed.visit(lexerParser.parse("A1")).value)

        with self.assertRaises(RecursionError):
            self.visitor_volatile.visit(lexerParser.parse("A1"))


class ContextBoundInterpreterWithFormulaAndValueCacheDereferencerTest(TestCase):

    def setUp(self) -> None:
        self.dereferencer = CachedDereferencer()
        self.visitor_fixed = \
            ContextBoundInterpreterVisitor(self.dereferencer, resolveVolatile=False)
        self.visitor_volatile= \
            ContextBoundInterpreterVisitor(self.dereferencer, resolveVolatile=True)
        self.helper = DereferencerHelper(self.dereferencer, writes_cache=True)

    def tearDown(self):
        del self.visitor_fixed
        del self.visitor_volatile
        del self.helper
        del self.dereferencer

    def test_ampsersand_of_visit_with_ref_to_empty(self):
        self.helper.writeStr("A1", "14")
        tree = lexerParser.parse('A1 & "-" & A3 & 1 & "A"') # empty node
        self.assertEqual("14-1A", self.visitor_volatile.visit(tree).value)

    def test_sum_of_visit_with_ref_to_empty(self):
        self.helper.writeNumber("A1", 14)
        tree = lexerParser.parse("A1 + A3 + 1") # empty node
        self.assertEqual(15, self.visitor_volatile.visit(tree).value)

    def test_cycle(self):
        self.dereferencer.write("A1", lexerParser.parse("A1"), None)
        self.assertEqual("A1", self.visitor_fixed.visit(lexerParser.parse("A1")).value)
        self.assertEqual(2, self.visitor_volatile.visit(lexerParser.parse("A1+2")).value)
