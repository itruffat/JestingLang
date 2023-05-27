from JestingLang.JParsing.JestingAST import InvalidValueNode, ReferenceValueNode
from JestingLang.Misc.JLogic.LogicFunctions import ref
from JestingLang.JVisitors.ContextfreeInterpreterVisitor import ContextfreeInterpreterVisitor


class ContextBoundInterpreterVisitor(ContextfreeInterpreterVisitor):

    """The complete syntax resolver, it requires a reference resolver to get the references when visiting stuff"""
    def __init__(self, context):
        super().__init__()
        self.contextResolver = context

    def visitRef(self, node):
        referenced = self.contextResolver.resolve(node.value)
        return InvalidValueNode("Broken reference") if referenced is None else referenced

    def visitIndirect(self, node):
        children_visited = node.children[0].accept(self)
        if children_visited.volatile():
            return children_visited
        reference = ref(children_visited.value)
        if reference is None:
            return InvalidValueNode("Bad reference")
        return ReferenceValueNode(reference).accept(self)

