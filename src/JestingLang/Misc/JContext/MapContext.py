from JestingLang.Misc.JContext.AbstractContext import AbstractContext
from JestingLang.JParsing.JestingAST import SimpleValueNode, Node, StrValueNode, IntValueNode


class MapContext(AbstractContext):
    """Example of a context, in this case by using a map for formulas respectively.
    This context does not support circular recursion and will freeze when trying to solve it.
    It also returns an error value if an unknown name is given."""

    def __init__(self):
        super().__init__()
        self.formulas = {}

    def resolve(self, name):
        if name not in self.formulas.keys():
            return None
        return self.formulas[name]

    def valueOf(self, node):
        if issubclass(type(node), SimpleValueNode):
            value = node.value
        else:
            value = node
        return value

    def write(self, key, formula):
        assert(issubclass(type(formula), Node))
        self.formulas[key] =formula

    def writeNumber(self, key, value):
        self.write(key, IntValueNode(value))

    def writeStr(self, key, value):
        self.write(key, StrValueNode(value))

    def show(self):
        _keys = set(self.formulas.keys())
        return {key: self.valueOf(self.resolve(key)) for key in _keys}
