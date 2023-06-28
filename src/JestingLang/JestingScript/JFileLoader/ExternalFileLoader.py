
class ExternalLoaderException(Exception):
    def __init__(self, *, on_open):
        self.on_open = on_open

class ExternalFileLoader:

    def __init__(self):
        self.loading = set()

    def _load(self, filename):
        with open(filename, "r") as open_file:
            file_data = open_file.read()
        return file_data

    def load(self, filename):
        if filename in self.loading:
            raise ExternalLoaderException(on_open=True)
        self.loading.add(filename)
        return self._load(filename)

    def unload(self, filename):
        if filename not in self.loading:
            raise ExternalLoaderException(on_open=False)
        self.loading.remove(filename)
