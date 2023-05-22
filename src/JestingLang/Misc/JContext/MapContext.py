from Misc.JContext.AbstractContext import AbstractContext
from JParsing.JestingAST import SimpleValueNode


class MapContext(AbstractContext):
    """Example of a context, in this case by using a map for formulas respectively"""

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

    def write(self, key, value):
        self.formulas[key] = value

    def show(self):
        _keys = set(self.formulas.keys())
        return {key: self.valueOf(self.resolve(key)) for key in _keys}
