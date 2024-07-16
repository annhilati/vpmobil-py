import xml.etree.ElementTree as XML
from .VpDay import VpDay, Klasse, Stunde

class Exceptions():
    """
    Enthält verschiedene Exceptions
    """

    class FetchingError(Exception):
        def __init__(self, message, status_code = None):
            self.message = message
            self.status_code = status_code
            super().__init__(self.message)

    class XMLParsingError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class XMLNotFound(XMLParsingError):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
