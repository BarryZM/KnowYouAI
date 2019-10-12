class Mission:
    def __init__(self, name, func):
        self.name = name
        self._func = func

    def run(self):
        self._func()