from JestingLang.JParsing.JestingAST import Node, EmptyValueNode

class ScriptNode(Node):
    def __init__(self, child):
        super().__init__()
        self.children = {0: child}

    def accept(self, visitor):
        return visitor.visitScript(self)

    def volatile(self):
        return False

    def addChild(self, new_child):
        self.children[len(self.children.keys())] = new_child
        return self

class TickNode(Node):
    def __init__(self, ticks):
        super().__init__()
        self.ticks = ticks

    def accept(self, visitor):
        return visitor.visitTick(self)

    def volatile(self):
        return False

class RawInputNode(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value[1:]

    def accept(self, visitor):
        return visitor.visitRawInput(self)

    def volatile(self):
        return False

class AssignNode(Node):
    def __init__(self, cell, statement):
        super().__init__()
        self.children = {0: cell, 1: statement}

    def accept(self, visitor):
        return visitor.visitAssignNode(self)

    def volatile(self):
        return False

class SetDefaultsNode(Node):
    def __init__(self, cell):
        super().__init__()
        self.children = {0: cell}

    def accept(self, visitor):
        return visitor.visitSetDefaultsNode(self)

    def volatile(self):
        return False


class PrintValueNode(Node):
    def __init__(self, *, cell=EmptyValueNode(), print_all=False):
        super().__init__()
        self.print_all = print_all
        self.children = {0: cell}

    def accept(self, visitor):
        return visitor.visitPrintValueNode(self)

    def volatile(self):
        return False