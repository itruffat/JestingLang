from abc import ABC, abstractmethod


class AbstractContext(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def resolve(self,name):
        pass

    @abstractmethod
    def valueOf(self,node):
        pass
