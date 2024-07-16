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

def getxml(object: VpDay | Klasse | Stunde) -> XML.ElementTree | XML.Element:
    """
    Gibt die XML Daten eines Objekts als Klasse des xml-Moduls zurück

    - object: VpDay -> ElementTree
    - object: Klasse -> Element
    - object: Stunde -> Element
    """
    if isinstance(object, VpDay): return object._datatree
    elif isinstance(object, Klasse): return object._data
    elif isinstance(object, Stunde): return object._data
    else: raise TypeError("object muss einer der Typen VpDay & Klasse sein") # Der Code ist ereichbar lol habs getestet