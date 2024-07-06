class FetchingError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class XMLError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)