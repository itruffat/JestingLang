from JestingLang.Core.JParsing.JestingAST import StrValueNode, IntValueNode


class DereferencerHelper:

    def __init__(self, deferencer, *,  writes_cache=True):
        self.deferencer = deferencer
        self.visitors = []
        self.single_write = not writes_cache

    def write(self, key, *kargs):
        if self.single_write:
            self.deferencer.write(key, kargs[0])
        else:
            self.deferencer.write(key, kargs[0], kargs[1])

    def writeNumber(self, key, value):
        self.write(key, IntValueNode(value), IntValueNode(value))

    def writeStr(self, key, value):
        self.write(key, StrValueNode(value), StrValueNode(value))