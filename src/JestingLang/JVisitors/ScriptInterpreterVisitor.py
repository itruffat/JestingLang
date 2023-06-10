from JestingLang.JVisitors.ContextfreeInterpreterVisitor import renodify
from JestingLang.JVisitors.ContextBoundInterpreterVisitor import ContextBoundInterpreterVisitor

class ScriptInterpreterVisitor(ContextBoundInterpreterVisitor):

    def visitTick(self, node):
        for _ in range(node.ticks):
            self.contextResolver.tick()

    def visitRawInput(self, node):
        raise Exception("Not implemented outside of ScriptJester")

    def visitAssignNode(self, node):
        raise Exception("Not implemented outside of ScriptJester")

    def visitSetDefaultsNode(self, node):
        raise Exception("Not implemented outside of ScriptJester")

    def visitPrintValueNode(self, node):
        raise Exception("Not implemented outside of ScriptJester")