from JParsing.JestingAST import InvalidValueNode, ReferenceValueNode

from JLogic.LogicFunctions import ref
from JVisitors.ContextfreeInterpreterVisitor import ContextfreeInterpreterVisitor

class JestingInterpreterVisitor(ContextfreeInterpreterVisitor):

    """The complete syntax resolver, it requires a reference resolver to get the references when visiting stuff"""
    def __init__(self):
        super().__init__()
        self.referenceResolver = None

    def visit(self, node, **kwords):
        self.referenceResolver = kwords.get("resolver")
        answer = super().visit(node)
        self.referenceResolver = None
        return answer

    def visitRef(self, node):
        referenced = self.referenceResolver(node.value)
        return InvalidValueNode("Broken reference") if referenced is None else referenced.get_value()

    def visitIndirect(self, node):
        children_visited = node.children[0].accept(self)
        if children_visited.volatile():
            return  children_visited
        reference = ref(children_visited.value)
        if reference is None:
            return InvalidValueNode("Bad reference")
        return ReferenceValueNode(reference).accept(self)

