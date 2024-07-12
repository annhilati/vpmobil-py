"""
A python module for interacting with a stundenplan24.de substitution plan
"""

from .Vertretungsplan import Vertretungsplan
from .VpDay import VpDay, Klasse, Stunde
from .workflow import Exceptions

class VpMobil:
    """
    Enthält nützliche Funktionen für den Arbeitsablauf

    #### Exceptions
    - FetchingError
    - XMLParsingError
        - XMLNotFound
    """
    FetchingError = Exceptions.FetchingError
    XMLNotFound = Exceptions.XMLNotFound
    XMLParsingError = Exceptions.XMLParsingError

__all__ = ['VpMobil', 'Vertretungsplan', 'VpDay', 'Klasse', 'Stunde']

    # Enthält alle Symbole, die bei "from vpmobil import" verfügbar sind
    # Enthält alle Symbole, die bei "from vpmobil import *" importiert werden