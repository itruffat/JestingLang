from JestingLang.Core.JDereferencer.CachedDereferencer import CachedDereferencer
from JestingLang.Core.JParsing.JestingAST import Node, StrValueNode, EmptyValueNode
from JestingLang.Misc.JLogic.LogicFunctions import extract_address


class CachedCellDereferencer(CachedDereferencer):
    """Same as CachedDeferencer but parsing the key to emulate workbooks, worksheets and cells.
    """

    def resolveReference(self, name):
        _, book, sheet, cell, _ = extract_address(name)
        if (book not in self.cache.keys() or self.cache[book] is None) or \
            (sheet not in self.cache[book].keys() or self.cache[book][sheet] is None) or \
            (cell not in self.cache[book][sheet].keys() or self.cache[book][sheet][cell] is None):
            return EmptyValueNode()
        return self.cache[book][sheet][cell]

    def write(self, key, formula, value=None):
        assert(issubclass(type(formula), Node))
        assert(value is None or issubclass(type(value), Node))
        _, book, sheet, cell, _ = extract_address(key)
        self.write_cell(book,sheet,cell, formula, value)

    def write_cell(self, book, sheet, cell, formula, value=None, update_which=0):
        assert(issubclass(type(formula), Node))
        assert(value is None or issubclass(type(value), Node))
        for array in (self.cache, self.memory):
            if book not in array.keys():
                array[book] = {}
            if sheet not in array[book].keys():
                array[book][sheet] = {}
            if cell not in array[book][sheet].keys():
                array[book][sheet][cell] = None
        if update_which in [0, 1]:
            self.memory[book][sheet][cell] = formula
        if update_which in [0, 2]:
            self.cache[book][sheet][cell] = value


if __name__ == "__main__":
    c = CachedCellDereferencer()
    c.write("A1", StrValueNode("12"), StrValueNode("12"))
    print(c.cache)
