from JestingLang.JestingScript.JFileLoader.ExternalFileLoader import ExternalFileLoader

class NonFileExternalFileLoader(ExternalFileLoader):

    def __init__(self, return_strings):
        super().__init__()
        self.return_strings = return_strings

    def _load(self, filename):
        return self.return_strings[filename]
