from abc import ABC, abstractmethod

class AbstractScriptManager(ABC):
    """
    """

    @abstractmethod
    def tick(self, visitor):
        pass

    @abstractmethod
    def write_formula(self, key, value):
        pass

    @abstractmethod
    def write_value(self, key, value):
        pass

    @abstractmethod
    def read(self, key, cache):
        pass

    @abstractmethod
    def read_all(self):
        pass

    @abstractmethod
    def set_default(self, default):
        pass

    @abstractmethod
    def set_local_defaults(self, default):
        pass

    @abstractmethod
    def open_file(self, filename):
        pass

    @abstractmethod
    def close_file(self, filename):
        pass

    @abstractmethod
    def make_alias(self, alias, cell):
        pass
