from JestingLang.JVisitors.ContextBoundInterpreterVisitor import ContextBoundInterpreterVisitor
from JestingLang.Misc.JContext.MapContext import MapContext
from JestingLang.Misc.JContext.MemoryContext import MemoryContext
from unittest import TestCase
import JestingLang.JParsing.LexerParser

parser = JestingLang.JParsing.LexerParser.parser


class contextBoundInterpreterTest(TestCase):

    def setUp(self) -> None:
        # Without formula memory
        self.context_without_formula = MapContext()
        self.visitor_without_formula_fixed = \
            ContextBoundInterpreterVisitor(self.context_without_formula, resolveVolatile=False)
        self.visitor_without_formula_volatile = \
            ContextBoundInterpreterVisitor(self.context_without_formula, resolveVolatile=True)
        # With formula memory
        self.context_with_formula = MemoryContext()
        self.visitor_with_formula_fixed = \
            ContextBoundInterpreterVisitor(self.context_with_formula, resolveVolatile=False)
        self.visitor_with_formula_volatile = \
            ContextBoundInterpreterVisitor(self.context_with_formula, resolveVolatile=True)

    def tearDown(self):
        del self.visitor_without_formula_fixed
        del self.visitor_without_formula_volatile
        del self.context_without_formula
        del self.visitor_with_formula_fixed
        del self.visitor_with_formula_volatile
        del self.context_with_formula

    def test_ampersand(self):
        tree = parser.parse("\"A\" & 1")
        self.assertEqual("A1", self.visitor_without_formula_fixed.visit(tree).value)

    def test_ampsersand_of_visit_with_ref_to_empty(self):
        self.context_with_formula.writeStr("A1", "14")
        tree = parser.parse('A1 & "-" & A3 & 1 & "A"') # empty node
        self.assertEqual("14-1A", self.visitor_with_formula_volatile.visit(tree).value)

    def test_visit_node(self):
        self.context_without_formula.writeNumber("A1", 12)
        tree = parser.parse("A1")
        self.assertEqual("A1", self.visitor_without_formula_fixed.visit(tree).value)
        self.assertEqual(12, self.visitor_without_formula_volatile.visit(tree).value)

    def test_indirect_visit_node(self):
        self.context_without_formula.writeNumber("A1", 16)
        tree = parser.parse("INDIRECT(\"A\" & 1)")
        self.assertEqual("IndirectNode", self.visitor_without_formula_fixed.visit(tree).__class__.__name__)
        self.assertEqual("A1", self.visitor_without_formula_fixed.visit(tree).children[0].value)
        self.assertEqual(16, self.visitor_without_formula_volatile.visit(tree).value)

    def test_sum_of_visit(self):
        self.context_without_formula.writeNumber("A1", 11)
        self.context_without_formula.writeNumber("A2", 19)
        tree = parser.parse("A1+A2")
        self.assertEqual("OperationNode", self.visitor_without_formula_fixed.visit(tree).__class__.__name__)
        self.assertEqual("+", self.visitor_without_formula_fixed.visit(tree).operation)
        self.assertEqual("A1",self.visitor_without_formula_fixed.visit(tree).children[0].value)
        self.assertEqual("A2",self.visitor_without_formula_fixed.visit(tree).children[1].value)
        self.assertEqual(30, self.visitor_without_formula_volatile.visit(tree).value)

    def test_sum_of_visit_with_ref(self):
        self.context_without_formula.writeNumber("A1", 14)
        tree = parser.parse("A1*2")
        self.context_without_formula.write("A2", tree)
        tree2 = parser.parse("1 + A2 + A1")
        self.assertEqual(43, self.visitor_without_formula_volatile.visit(tree2).value)

    def test_sum_of_visit_with_ref_to_empty(self):
        self.context_with_formula.writeNumber("A1", 14)
        tree = parser.parse("A1 + A3 + 1") # empty node
        self.assertEqual(15, self.visitor_with_formula_volatile.visit(tree).value)

    def test_sum_of_visit_with_ref_and_changes(self):
        self.context_without_formula.writeNumber("A1", 12)
        self.context_without_formula.write("A2", parser.parse("A1*2"))
        self.assertEqual(37, self.visitor_without_formula_volatile.visit(parser.parse("1 + A2 + A1")).value)
        self.context_without_formula.writeNumber("A1", 10)
        self.assertEqual(31, self.visitor_without_formula_volatile.visit(parser.parse("1 + A2 + A1")).value)

    def test_double_indirection(self):
        self.context_without_formula.writeNumber("A1", 12)
        self.context_without_formula.write("A2", parser.parse("A1"))
        self.context_without_formula.write("A3", parser.parse("A2"))
        self.assertEqual(12, self.visitor_without_formula_volatile.visit(parser.parse("A3")).value)
        self.context_without_formula.writeNumber("A1", 10)
        self.assertEqual(10, self.visitor_without_formula_volatile.visit(parser.parse("A3")).value)

    def test_cycle(self):
        self.context_without_formula.write("A1", parser.parse("A1"))
        self.assertEquals("A1", self.visitor_without_formula_fixed.visit(parser.parse("A1")).value)

        with self.assertRaises(RecursionError):
            self.visitor_without_formula_volatile.visit(parser.parse("A1"))

        self.context_with_formula.write("A1", parser.parse("A1"), None)
        self.assertEqual("A1", self.visitor_with_formula_fixed.visit(parser.parse("A1")).value)
        self.assertEqual(2, self.visitor_with_formula_volatile.visit(parser.parse("A1+2")).value)
