from JestingLang.Core.JParsing.JestingAST import EmptyValueNode
from JestingLang.Core.JDereferencer.CachedCellDereferencer import CachedCellDereferencer
from JestingLang.JestingScript.JScriptManager.AbstractScriptManager import AbstractScriptManager
from JestingLang.Misc.JLogic.LogicFunctions import extract_address


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

class SDCantResolveAliasException(SDException):
    pass

class SDUnknownRuleReferenced(SDException):
    pass

class SDRuleNeverReferencesAddress(SDException):
    pass

class SDUnlockingUnlockedAddress(SDException):
    pass

class SDLockingLockedAddress(SDException):
    pass

class ScriptDereferencer(CachedCellDereferencer, AbstractScriptManager):
    """
    """

    def __init__(self, memory = None, cache = None, require_open = True):
        super().__init__(memory, cache)
        self.open_files = set()
        self.aliases = {}
        self.reverse_aliases = {}
        self.rules = {}
        self.locked_addresses = set()
        self.default_book = None
        self.default_sheet = None
        self.default_cell = None
        self.local_book = None
        self.local_sheet = None
        self.require_open = require_open

    def _parse(self, _name, check_aliases = True):
        if _name in self.aliases.keys() and check_aliases:
            path, book, sheet, cell, final = self.aliases[_name]
        else:
            path, book, sheet, cell, final = extract_address(_name)
            if cell is None:
                path, book, sheet, cell, final = None, None, None, None, None
            else:
                book = book if book is not None else self.local_book
                book = book if book is not None else self.default_book
                sheet = sheet if sheet is not None else self.local_sheet
                sheet = sheet if sheet is not None else self.default_sheet
                cell = cell if cell is not None else self.default_cell
        return path, book, sheet, cell, final

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

        self._unset_local_defaults()  # Remove the local
        keys = list(self.cache.keys())
        for k in keys:
            del self.cache[k]
        for k in new_cache.keys():
            self.cache[k] = new_cache[k]

    def parse_key(self, key, require_open):
        _, book, sheet, cell, _ = self._parse(key)
        if require_open and book not in self.open_files:
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
        return (self.cache[book][sheet][cell], self.memory[book][sheet][cell])

    def read_all(self):
        list_of_cells = []
        for book in self.memory.keys():
            for sheet in self.memory[book].keys():
                for cell in self.memory[book][sheet].keys():
                    if type(self.memory[book][sheet][cell]) is not EmptyValueNode:
                        list_of_cells.append((book,sheet,cell))
        list_of_cells.sort()
        answer = []
        for book, sheet, cell in list_of_cells:
            self._set_local_defaults(book=book, sheet=sheet) # Each node is resolved with itself as local
            answer.append(((book,sheet,cell), self.cache[book][sheet][cell], self.memory[book][sheet][cell],))
        return answer

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
        if _filename not in self.open_files:
            self.open_files.add(_filename)
            if _filename not in self.memory.keys():
                self.memory[_filename] = {}
            if _filename not in self.cache.keys():
                self.cache[_filename] = {}
        else:
            raise SDOpenFileException(_filename)

    def close_file(self, _filename):
        if _filename in self.open_files:
            self.open_files.remove(_filename)
        else:
            raise SDClosingUnopenedException(_filename)

    def make_alias(self, alias, cell):
        parsed_cell = self._parse(cell, check_aliases = False)

        if None in parsed_cell[1:4]:  # Doesn't have a book, a sheet or a initial cell
            pb, ps, pc = parsed_cell[1:4]
            raise SDCantResolveAliasException(f"Either book ({pb}), sheet ({ps}) or cell ({pc}) are not defined")

        if parsed_cell in self.reverse_aliases.keys():
            previous_cell_alias = self.reverse_aliases[parsed_cell]
            del self.aliases[previous_cell_alias]
            del self.reverse_aliases[parsed_cell]

        self.aliases[alias] = parsed_cell
        self.reverse_aliases[parsed_cell] = alias

    def add_address_to_rule(self, rule, address):
        if rule not in self.rules.keys():
            raise SDUnknownRuleReferenced(f"Adding cell to unknown rule ({rule})")
        statement_and_color, addresses = self.rules[rule]
        addresses.add(address)
        self.rules[rule] = (statement_and_color, addresses)

    def remove_address_from_rule(self, rule, address):
        if rule not in self.rules.keys():
            raise SDUnknownRuleReferenced(f"Trying to remove cell from unknown rule ({rule})")
        if address not in self.rules[rule][1]:
            raise SDRuleNeverReferencesAddress(f"Invalid reference made on delete ({rule}~>{address})")
        statement_and_color, addresses  = self.rules[rule]
        addresses.remove(address)
        self.rules[rule] = (statement_and_color, addresses)

    def update_rule(self, rule, statement_and_color):
        if rule not in self.rules.keys():
            addresses = set()
        else:
            _, addresses = self.rules[rule]
        self.rules[rule] = (statement_and_color, addresses)

    def delete_rule(self, rule):
        if rule not in self.rules.keys():
            raise SDUnknownRuleReferenced(f"Trying to delete a non existing rule ({rule})")
        del self.rules[rule]

    def lock_address(self, address):
        if address in self.locked_addresses:
            raise SDLockingLockedAddress("")
        self.locked_addresses.add(address)

    def unlock_address(self, address):
        if address not in self.locked_addresses:
            raise SDUnlockingUnlockedAddress("")
        self.locked_addresses.remove(address)

if __name__ == "__main__":
    #c = CachedCellDereferencer()
    pass
    #c.write("A1", StrValueNode("12"), StrValueNode("12"))
    #print(c.cache)
