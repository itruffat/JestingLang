from JVisitors.AbstractJestingVisitor import AbstractJestingVisitor


class PrintingVisitor(AbstractJestingVisitor):

    def visit(self, node):
        print(node.accept(self))
        return None

    def visitSimple(self,node):
        return node.value

    def visitOperation(self,node):
        return "({},{})".format(node.operation,
        ",".join(map(lambda n: str(n.accept(self)), node.children.values())))

    def visitIf(self,node):
        return "IF({})THEN({})ELSE({})".format(node.children[0].accept(self), node.children[1].accept(self), node.children[2].accept(self))

    def visitIndirect(self, node):
        return "INDIRECT({})".format(node.children[0].accept(self))


class TreePrinter(AbstractJestingVisitor):

    def visit(self, node):
        printable_tree = node.accept(self)
        self.treePrint(printable_tree, 0)

        return None

    def treePrint(self, node, depth, finished=()):
        parent_finished = depth - 1 in finished
        printing_depth = depth
        while printing_depth > 0:
            if parent_finished and printing_depth == 1:
                print(" L", end='')
            elif depth - printing_depth not in finished:
                print(" |", end='')
            else:
                print("  ", end='')
            printing_depth-= 1
        print("__" if parent_finished else "--", end='')
        print(node[0] if not node[2] else "[${}]".format(node[0]))
        children = len(node[1])
        for child in node[1]:
            children -= 1
            new_finished = finished + (tuple([depth]) if children == 0 else ())
            self.treePrint(child, depth+1, new_finished)

    def visitSimple(self,node):
        return str(node.value), [], node.volatile()

    def visitInvalid(self, node):
        return "[INVALID: {}]".format(str(node.value.comment)), [], node.volatile()

    def visitOperation(self,node):
        return node.operation, list(map(lambda n: (n.accept(self)), node.children.values())), node.volatile()

    def visitIf(self,node):
        return "IF", (node.children[0].accept(self), node.children[1].accept(self), node.children[2].accept(self)), node.volatile()

    def visitIndirect(self, node):
        return "INDIRECT", [node.children[0].accept(self)], node.volatile()