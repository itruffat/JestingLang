from JestingLang.Core.JParsing.JestingAST import EmptyValueNode
from JestingLang.JestingScript.JDereferencer.AbstractScriptDereferencer import AbstractScriptDereferencer
from JestingLang.Misc.JLogic.LogicFunctions import address as address_regex


class SDException(BaseException):
    def __init__(self,msg):
        super().__init__()
        self.msg = msg

class SDOpenFileException(SDException):
    pass

class SDWritingUnopenedException(SDException):
    pass

class SDClosingUnopenedException(SDException):
    pass

class ScriptDereferencer(AbstractScriptDereferencer):
    """
    """

    def __init__(self, memory = None, cache = None, require_open = True):
        super().__init__(memory, cache)
        self.open_files = {}
        self.default_book = None
        self.default_sheet = None
        self.default_cell = None
        self.local_book = None
        self.local_sheet = None
        self.require_open = require_open

    def _parse(self, name):
        match = address_regex.match(name)
        if match is None:
            return None, None, None, None, None
        else:
            matches = match.groupdict()
            book = matches['workbook'] if matches['workbook'] is not None else self.local_book
            book = book if book is not None else self.default_book
            sheet = matches['worksheet'] if matches['worksheet'] is not None else self.local_sheet
            sheet = sheet if sheet is not None else self.default_sheet
            cell = matches['initial'] if matches['initial'] is not None else self.default_cell
            return matches['path'], book, sheet, cell, matches['final']

    def tick(self, visitor):
        new_cache = {}
        for book in self.memory.keys():
            new_cache[book] = {}
            for sheet in self.memory[book].keys():
                new_cache[book][sheet] = {}
                for cell in self.memory[book][sheet].keys():
                    if type(self.memory[book][sheet][cell]) is not EmptyValueNode:
                        self._set_local_defaults(book=book, sheet=sheet) # Each node is resolved with itself as local
                        new_cache[book][sheet][cell] = visitor.visit(self.memory[book][sheet][cell])
                    else:
                        if book in self.cache.keys() and sheet in self.cache[book].keys():
                            new_cache[book][sheet][cell] = self.cache[book][sheet].get(cell, EmptyValueNode())
        self._unset_local_defaults() # Remove the local
        keys = list(self.cache.keys())
        for k in keys:
            del self.cache[k]
        for k in new_cache.keys():
            self.cache[k] = new_cache[k]

    def parse_key(self, key, require_open):
        _, book, sheet, cell, _ = self._parse(key)
        if require_open and book not in self.open_files.keys():
            raise SDWritingUnopenedException(book)
        return book, sheet, cell

    def write_formula(self, key, value):
        book, sheet, cell = self.parse_key(key, require_open=self.require_open)
        self.write_cell(book, sheet, cell, value, None)
        self._unset_local_defaults()

    def write_value(self, key, value):
        book, sheet, cell = self.parse_key(key, require_open=self.require_open)
        self.write_cell(book, sheet, cell, value, value, update_which=2)
        self._unset_local_defaults()

    def read(self, key, cache=True):
        book, sheet, cell = self.parse_key(key, require_open=False)
        self._unset_local_defaults()
        return self.cache[book][sheet][cell] if cache else self.memory[book][sheet][cell]

    def read_all(self):
        pass

    def set_default(self, default):
        _, book, sheet, cell, _ = self._parse(default)
        self.default_book = book
        self.default_sheet = sheet
        self.default_cell = cell

    def set_local_defaults(self, defaults):
        _, book, sheet, _, _ = self._parse(defaults)
        self._set_local_defaults(book, sheet)

    def _set_local_defaults(self, book, sheet):
        self.local_book = book
        self.local_sheet = sheet

    def _unset_local_defaults(self):
        self.local_book = None
        self.local_sheet = None

    def open_file(self, _filename):
        if _filename not in self.open_files.keys():
            self.open_files[_filename] = 0
            if _filename not in self.memory.keys():
                self.memory[_filename] = {}
            if _filename not in self.cache.keys():
                self.cache[_filename] = {}
        else:
            raise SDOpenFileException(_filename)

    def close_file(self, _filename):
        if _filename in self.open_files.keys():
            del self.open_files[_filename]
        else:
            raise SDClosingUnopenedException(_filename)


if __name__ == "__main__":
    #c = CachedCellDereferencer()
    pass
    #c.write("A1", StrValueNode("12"), StrValueNode("12"))
    #print(c.cache)
