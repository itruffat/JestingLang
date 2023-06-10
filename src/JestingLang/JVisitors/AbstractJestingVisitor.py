from abc import ABC, abstractmethod


class AbstractJestingVisitor(ABC):

    def __init__(self):
        pass

    def visit(self, node):
        return node.accept(self)

    @abstractmethod
    def visitSimple(self, node):
        return None

    def visitEmpty(self, node):
        return None

    def visitInvalid(self, node):
        return None

    def visitStr(self, node):
        return None

    def visitInt(self, node):
        return None

    def visitDate(self, node):
        return None

    def visitBool(self, node):
        return None

    def visitRef(self, node):
        return None

    def visitOperation(self, node):
        return None

    def visitIf(self, node):
        return None

    def visitIndirect(self, node):
        return None

    def visitTick(self, node):
        raise Exception("Not implemented outside of ScriptJester")

    def visitRawInput(self, node):
        raise Exception("Not implemented outside of ScriptJester")

    def visitAssignNode(self, node):
        raise Exception("Not implemented outside of ScriptJester")

    def visitSetDefaultsNode(self, node):
        raise Exception("Not implemented outside of ScriptJester")

    def visitPrintValueNode(self, node):
        raise Exception("Not implemented outside of ScriptJester")
