"""
A python module for interacting with a stundenplan24.de substitution plan
"""

from .Vertretungsplan import Vertretungsplan
from .VpDay import VpDay, Klasse, Stunde, getxml
from .workflow import Exceptions

__all__ = ['VpMobil', 'Vertretungsplan', 'VpDay', 'Klasse', 'Stunde']
    # Enthält alle Symbole, die bei "from vpmobil import" verfügbar sind
    # Enthält alle Symbole, die bei "from vpmobil import *" importiert werden

class VpMobil:
    """
    Enthält nützliche Funktionen für den Arbeitsablauf

    #### Funktionen
    - getxml()
    #### Exceptions
    - .FetchingError
    - .XMLParsingError
        - .XMLNotFound
    """
    getxml = getxml
    
    FetchingError = Exceptions.FetchingError
    XMLNotFound = Exceptions.XMLNotFound
    XMLParsingError = Exceptions.XMLParsingError

