from JestingLang.Core.JDereferencer.AbstractDereferencer import AbstractDereferencer
from JestingLang.Core.JParsing.JestingAST import SimpleValueNode, Node


class KeyValueDereferencer(AbstractDereferencer):
    """Example of a deferencer, in this case by using a map for formulas respectively. (as simple as it gets)

    This deferencer does not support circular recursion and will freeze when trying to solve it.
    It also returns an error value if an unknown name is given.
    """

    def __init__(self, memory=None):
        super().__init__()
        if memory is not None:
            self.memory = memory
        else:
            self.memory = {}

    def resolveReference(self, name):
        if name not in self.memory.keys():
            return None
        return self.memory[name]

    def valueOf(self, node):
        if issubclass(type(node), SimpleValueNode):
            value = node.value
        else:
            value = node
        return value

    def write(self, key, formula, value=None):
        assert(issubclass(type(formula), Node))
        assert(value is None)
        self.memory[key] =formula

    def show(self):
        _keys = set(self.memory.keys())
        return {key: self.valueOf(self.resolveReference(key)) for key in _keys}
