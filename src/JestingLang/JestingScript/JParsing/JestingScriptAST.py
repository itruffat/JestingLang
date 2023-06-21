from JestingLang.Core.JParsing.JestingAST import Node, EmptyValueNode

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
        self.value = value

    def accept(self, visitor):
        return visitor.visitRawInput(self)

    def volatile(self):
        return False

class AssignNode(Node):
    def __init__(self, cell, statement):
        super().__init__()
        self.target = cell
        self.children = {0: statement}

    def accept(self, visitor):
        return visitor.visitAssign(self)

    def volatile(self):
        return False

class SetDefaultsNode(Node):
    def __init__(self, cell):
        super().__init__()
        self.children = {0: cell}

    def accept(self, visitor):
        return visitor.visitSetDefaults(self)

    def volatile(self):
        return False


class PrintValueNode(Node):
    def __init__(self, *, cell=EmptyValueNode(), print_all=False, print_value=False):
        super().__init__()
        self.print_all = print_all
        self.print_value = print_value
        self.children = {0: cell}

    def accept(self, visitor):
        return visitor.visitPrintValue(self)

    def volatile(self):
        return False

class OpenCloseFileNode(Node):
    def __init__(self, value, *, do_open):
        super().__init__()
        self.value = value
        self.do_open = do_open

    def accept(self, visitor):
        return visitor.visitOpenCloseFile(self)

    def volatile(self):
        return False