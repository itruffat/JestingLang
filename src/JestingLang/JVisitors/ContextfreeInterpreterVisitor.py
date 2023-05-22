from JParsing.JestingAST import IntValueNode, StrValueNode, ReferenceValueNode, BoolValueNode, \
                                              OperationNode, IfNode, InvalidValueNode, \
                                              ToleratedErrorNode
from Misc.JLogic.LogicFunctions import boolean
from JVisitors.AbstractJestingVisitor import AbstractJestingVisitor
from Misc.JLogic.OperationMapping import operations

def renodify(value, label):
    if label == "INT":
        return IntValueNode(int(value))
    if label == "STR":
        return StrValueNode(str(value))
    if label == "REF":
        return ReferenceValueNode(str(value))
    if label == "BOOL":
        return BoolValueNode(bool(value))


class ContextfreeInterpreterVisitor(AbstractJestingVisitor):

    """The basic resolver for the syntax, does not depend on anything besides itself but can't resolve references"""

    def visit(self, node):
        return node.accept(self)

    def visitSimple(self, node):
        return node

    def visitOperation(self, node):
        visitedChildren = {k: v.accept(self) for k, v in node.children.items()}
        if any(map(lambda c:c.volatile(), visitedChildren.values())):
            answer = OperationNode(node.operation, visitedChildren)
        else:
            variables = {k : v.value for k,v in visitedChildren.items()}
            errors, value, label = operations[node.operation](variables = variables)
            if len(errors) == 0:
                answer = renodify(value, label)
            else:
                answer = InvalidValueNode(",".join(errors))
        return answer

    def visitIf(self, node):
        _if = node.children[0].accept(self)
        _then = node.children[1].accept(self)
        _else = node.children[2].accept(self)

        if _if.volatile():
            answer = IfNode(_if,_then,_else)
        else:
            # This behaviour is not real since spreedsheets don't use short-circuit (for whatever reason)
            if boolean(_if.value) and not _then.volatile():
               answer = _then
            elif not boolean(_if.value) and not _else.volatile():
                answer = _else
            else:
                answer = IfNode(_if,_then,_else)

        return answer

    def visitRef(self, node):
        return ToleratedErrorNode(node.value, "CONTEXT FREE, NOT IMPLEMENTED")

    def visitIndirect(self, node):
        children_visited = node.children[0].accept(self)
        return ToleratedErrorNode(children_visited, "CONTEXT FREE, NOT IMPLEMENTED")
