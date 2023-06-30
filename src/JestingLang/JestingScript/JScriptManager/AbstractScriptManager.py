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

    @abstractmethod
    def add_address_to_rule(self, rule, address):
        pass

    @abstractmethod
    def remove_address_from_rule(self, rule, address):
        pass

    @abstractmethod
    def update_rule(self, rule, statement_and_color):
        pass

    @abstractmethod
    def delete_rule(self,rule):
        pass

    @abstractmethod
    def lock_address(self, address):
        pass

    @abstractmethod
    def unlock_address(self, address):
        pass
