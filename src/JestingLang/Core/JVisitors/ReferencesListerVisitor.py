from JestingLang.Core.JVisitors.AbstractJestingVisitor import AbstractJestingVisitor


class ReferencesListerVisitor(AbstractJestingVisitor):

    def extract_children(self, old_children):
        children = []
        for v in old_children.values():
            child = v.accept(self)
            children += child
        return children

    def visit(self, node):
        if node.volatile():
            return node.accept(self)

    def visitSimple(self, node):
        return []

    def visitEmpty(self, node):
        return []

    def visitInvalid(self, node):
        return []

    def visitStr(self, node):
        return []

    def visitInt(self, node):
        return []

    def visitDate(self, node):
        return []

    def visitBool(self, node):
        return []

    def visitRef(self, node):
        return [node.value]

    def visitOperation(self, node):
        if node.volatile():
            return self.extract_children(node.children)

    def visitIf(self, node):
        if node.volatile():
            return self.extract_children(node.children)

    def visitIndirect(self, node):
        return []
        #if node.volatile():
            #return self.extract_children(node.children)
