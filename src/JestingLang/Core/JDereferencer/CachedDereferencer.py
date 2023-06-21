from JestingLang.Core.JParsing.JestingAST import Node, EmptyValueNode
from JestingLang.Core.JDereferencer.KeyValueDereferencer import KeyValueDereferencer

class CachedDereferencer(KeyValueDereferencer):
    """Example of a deferencer, more similar to how a real spreadsheet would work than KeyValueDeferencer.

    Here an undefined reference returns empty value (which will later translate into '' ) and
    iteration looks at memory instead of looking at the formula.
    """

    def __init__(self, memory = None, cache = None):
        super().__init__(memory)
        if cache is not None:
            self.cache = cache
        else:
            self.cache = {}

    def resolveReference(self, name):
        if name not in self.cache.keys() or self.cache[name] is None:
            return EmptyValueNode()
        return self.cache[name]

    def write(self, key, formula, value=None):
        assert(issubclass(type(formula), Node))
        assert(value is None or issubclass(type(value), Node))
        self.cache[key] = value
        self.memory[key] = formula