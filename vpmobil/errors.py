class NoDataError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class XMLError(Exception):
    der __init__(self, message):
        self.message = message
        super().__init__(self.message)