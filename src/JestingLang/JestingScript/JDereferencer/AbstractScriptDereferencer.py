from abc import ABC
from JestingLang.Core.JDereferencer.CachedCellDereferencer import CachedCellDereferencer


class AbstractScriptDereferencer(CachedCellDereferencer):
    """
    """

    def tick(self, visitor):
        pass

    def write_formula(self, key, value):
        pass

    def write_value(self, key, value):
        pass

    def read(self, key, cache):
        pass

    def read_all(self):
        pass

    def set_default(self, default):
        pass

    def set_local_defaults(self, default):
        pass

    def open_file(self, filename):
        pass

    def close_file(self, filename):
        pass
