from JestingLang.JParsing.JestingAST import SimpleValueNode, Node, StrValueNode, IntValueNode, EmptyValueNode
from JestingLang.Misc.JContext.MapContext import MapContext

class MemoryContext(MapContext):
    """Example of a context, more similar to how a real spreadsheet would work.
    Here an undefined reference returns empty value (which will later translate into '' ) and
    iteration looks at memory instead of looking at the formula.
    """

    def __init__(self):
        super().__init__()
        self.memory = {}

    def resolve(self, name):
        if name not in self.memory.keys() or self.memory[name] is None:
            return EmptyValueNode()
        return self.memory[name]

    def write(self, key, formula, value=None):
        assert(issubclass(type(formula), Node))
        assert(value is None or issubclass(type(value), Node))
        self.memory[key] = value
        self.formulas[key] = formula

    def writeNumber(self, key, value):
        self.write(key, IntValueNode(value), IntValueNode(value))

    def writeStr(self, key, value):
        self.write(key, StrValueNode(value), StrValueNode(value))

    def updateWith(self, function):
        for key in sorted(self.formulas.keys()):
            formula = self.formulas[key]
            updated_value = function(formula, self)
            self.write(key, formula, updated_value)
