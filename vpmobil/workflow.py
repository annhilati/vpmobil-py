class Exceptions():
    """
    Enthält verschiedene Exceptions
    """

    class FetchingError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class XMLParsingError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class XMLNotFound(XMLParsingError):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)