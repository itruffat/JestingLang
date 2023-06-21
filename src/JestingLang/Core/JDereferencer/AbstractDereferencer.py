from abc import ABC, abstractmethod


class AbstractDereferencer(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def resolveReference(self,name):
        pass

    @abstractmethod
    def valueOf(self, node):
        pass

    @abstractmethod
    def write(self, key, formula, value):
        pass
