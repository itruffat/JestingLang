from JestingLang.Core.JVisitors.ContextfreeInterpreterVisitor import renodify
from JestingLang.Core.JVisitors.ContextBoundInterpreterVisitor import ContextBoundInterpreterVisitor
from JestingLang.Misc.JLogic.LogicFunctions import label_data
from JestingLang.Core.JParsing.JestingAST import EmptyValueNode
from JestingLang.JestingScript.JParsing.JestingScriptAST import RawInputNode
from JestingLang.JestingScript.JScriptManager.AbstractScriptManager import AbstractScriptManager
from JestingLang.Core.JDereferencer.AbstractDereferencer import AbstractDereferencer
from sys import stdout

class ScriptInterpreterVisitor(ContextBoundInterpreterVisitor):

    def __init__(self,
                 dereferencer: AbstractDereferencer,
                 resolveVolatile,
                 scriptManager: AbstractScriptManager = None,
                 insertionUpdate = True,
                 output = None):

        super().__init__(dereferencer, resolveVolatile)
        self.scriptManager = scriptManager if scriptManager is not None else dereferencer
        self.insertionUpdate = insertionUpdate
        self.default_book = None
        self.default_sheet = None
        self.default_cell = None
        self.output = output if output is not None else stdout

    def visitScript(self, node):
        for n, sub_node in node.children.items():
            self.visit(sub_node)

    def visitTick(self, node):
        for _ in range(node.ticks):
            self.scriptManager.tick(self)

    def visitAlias(self, node):
        self.scriptManager.make_alias(node.target, node.source)

    def visitRawInput(self, node):
        data = node.value
        label = label_data(data)
        return renodify(data, label)

    def visitAssign(self, node):
        cell = node.target
        self.scriptManager.set_local_defaults(cell)
        if type(node.children[0]) is RawInputNode:
            data = node.children[0].accept(self)
            self.scriptManager.write_formula(cell, EmptyValueNode())
            self.scriptManager.write_value(cell, data)
        else:
            child = node.children[0]
            self.scriptManager.write_formula(cell, child)
            if (not child.volatile()) or (self.resolveVolatile and self.insertionUpdate):
                self.scriptManager.write_value(cell, child.accept(self))
            else:
                self.scriptManager.write_value(cell, EmptyValueNode())

    def visitSetDefaults(self, node):
        cell = node.reference
        self.scriptManager.set_default(cell)

    def visitPrintValue(self, node):
        if node.print_all:
            self.output.write(self.scriptManager.read_all())
        else:
            cell = node.children[0]
            if node.print_value:
                self.output.write(str(self.scriptManager.read(cell, True)))
            else:
                self.output.write(str(self.scriptManager.read(cell, False)))
        self.output.write("\n")

    def visitOpenCloseFile(self, node):
        file_name = node.value
        if node.do_open:
            self.scriptManager.open_file(file_name)
        else:
            self.scriptManager.close_file(file_name)
            