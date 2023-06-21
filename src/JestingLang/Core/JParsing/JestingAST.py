from abc import ABC, abstractmethod

operations = {"+","-","*","/","&","=",'>','NOT','AND','OR', "u-"}

class Node(ABC):
    def __init__(self):
        self.children = {}

    @abstractmethod
    def accept(self, visitor):
        pass

    @abstractmethod
    def volatile(self):
        pass

class SimpleValueNode(Node, ABC):
    def __init__(self, value):
        super().__init__()
        self.name = ""
        self.value = value

    def accept(self, visitor):
        return visitor.visitSimple(self)

    #def __str__(self):
        #return f"{self.name}:{str(self.value)}"


class EmptyValueNode(SimpleValueNode):
    def __init__(self):
        self.name = "empty"
        super().__init__(None)

    def accept(self, visitor):
        child = visitor.visitEmpty(self)
        return super().accept(visitor) if child is None else child

    def volatile(self):
        return False


class InnerError():

    def __init__(self, comment):
        self.comment = comment

    def isNA(self):
        return False


class NAError():

    def __init__(self):
        self.comment = "#NA"

    def isNA(self):
        return True


class InvalidValueNode(SimpleValueNode):

    def __init__(self, value):
        self.name = "INVALID"
        super().__init__(NAError() if value == "#NA" else InnerError(value))

    def accept(self, visitor):
        child = visitor.visitInvalid(self)
        return super().accept(visitor) if child is None else child

    def volatile(self):
        return not self.value.isNA()


class StrValueNode(SimpleValueNode):

    def accept(self, visitor):
        self.name = "str"
        child = visitor.visitStr(self)
        return super().accept(visitor) if child is None else child

    def volatile(self):
        return False


class IntValueNode(SimpleValueNode):

    def accept(self, visitor):
        self.name = "Integer"
        child = visitor.visitInt(self)
        return super().accept(visitor) if child is None else child

    def volatile(self):
        return False


class BoolValueNode(SimpleValueNode):

    def accept(self, visitor):
        self.name = "Boolean"
        child = visitor.visitBool(self)
        return super().accept(visitor) if child is None else child

    def volatile(self):
        return False


class DateValueNode(SimpleValueNode):

    def accept(self, visitor):
        self.name = "Date"
        child = visitor.visitDate(self)
        return super().accept(visitor) if child is None else child

    def volatile(self):
        return False


class ReferenceValueNode(SimpleValueNode):

    def accept(self, visitor):
        self.name = "Ref"
        child = visitor.visitRef(self)
        return super().accept(visitor) if child is None else child

    def volatile(self):
        return True

class OperationNode(Node):
    def __init__(self, operation, children):
        super().__init__()
        self.operation = operation
        assert (operation in operations)
        self.children = children

    def accept(self, visitor):
        return visitor.visitOperation(self)

    def volatile(self):
        return any(map(lambda c: c.volatile(), self.children.values()))

    #def __str__(self):
        #return f"Operation({str(self.operation)}):{','.join(map(lambda x:str(x), self.children))}"


class IfNode(Node):
    def __init__(self, _if, _then, _else):
        super().__init__()
        self.children = {0: _if, 1: _then, 2: _else}

    def accept(self, visitor):
        return visitor.visitIf(self)

    def volatile(self):
        return any(map(lambda c: c.volatile(), self.children.values()))

class BooleanOperationNode(Node):
    def __init__(self, _operation, * _children):
        super().__init__()
        self.operation = _operation
        self.children = {n:c for n,c in enumerate(_children)}

    def accept(self, visitor):
        return visitor.visitBooleanOperator(self)

    def volatile(self):
        return any(map(lambda c: c.volatile(), self.children.values()))

class IndirectNode(Node):
    def __init__(self, child):
        super().__init__()
        self.children = {0: child}

    def accept(self, visitor):
        return visitor.visitIndirect(self)

    def volatile(self):
        return True

class ToleratedErrorNode(Node): # Used to catch for not implemented errors

    def __init__(self, value, error_msg):
        super().__init__()
        self.value = value
        self.error_msg = error_msg

    def volatile(self):
        return False

    def accept(self, visitor):
        return visitor.visitToleratedError(self)
