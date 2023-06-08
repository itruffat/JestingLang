from JestingLang.JParsing.JestingAST import InvalidValueNode, ReferenceValueNode, IndirectNode
from JestingLang.Misc.JLogic.LogicFunctions import ref
from JestingLang.JVisitors.ContextfreeInterpreterVisitor import ContextfreeInterpreterVisitor


class ContextBoundInterpreterVisitor(ContextfreeInterpreterVisitor):

    """The complete syntax resolver, it requires a reference resolver to get the references when visiting stuff"""
    def __init__(self, context, resolveVolatile):
        super().__init__(resolveVolatile)
        self.contextResolver = context

    def visitRef(self, node):
        if node.volatile and (not self.resolveVolatile):
            return node
        referencedNode = self.contextResolver.resolve(node.value)
        return InvalidValueNode("Broken reference") if referencedNode is None else referencedNode.accept(self)

    def visitIndirect(self, node):
        children_visited = node.children[0].accept(self)
        if (not self.resolveVolatile) and children_visited.volatile():
            return IndirectNode(children_visited)
        reference = ref(children_visited.value)
        if reference is None:
            return InvalidValueNode("Bad reference")
        if not self.resolveVolatile:
            return IndirectNode(children_visited)
        return ReferenceValueNode(reference).accept(self)

