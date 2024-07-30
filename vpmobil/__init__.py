"""
A python wrapper package for interacting with a stundenplan24.de substitution plan
"""

from .fetcher import Vertretungsplan
from .parser import VpDay, Klasse, Stunde
from .io import getxml, parsefromfile

__all__ = ['VpMobil', 'Vertretungsplan', 'VpDay', 'Klasse', 'Stunde']
    # Enthält alle Symbole, die bei "from vpmobil import" verfügbar sind
    # Enthält alle Symbole, die bei "from vpmobil import *" importiert werden

class VpMobil:
    """
    Enthält nützliche Funktionen für den Arbeitsablauf

    #### Funktionen
        getxml(): Isoliert die XML-Datenobjekte eines VpMobil-Objekts
        parsefromfile(): Läd die XML-Daten einer Datei in ein VpDay-Objekt

    #### Exceptions
        FetchingError: Wenn Daten nicht abgerufen werden können
            InvalidCredentialsError: Wenn die angegebene Anmeldedaten ungültig sind
            SchulnummerNotFoundError: Wenn die angegebene Schulnummer nicht registriert ist
        XMLParsingError: Wenn XML-Daten nicht richtig ausgewertet werden können
            XMLNotFound: Wenn ein Element der XML-Daten nicht gefunden werden kann
    """

    getxml = getxml
    parsefromfile = parsefromfile
    
    from .exceptions import FetchingError, XMLNotFound, XMLParsingError, InvalidCredentialsError, SchulnummerNotFoundError
    FetchingError = FetchingError
    XMLNotFound = XMLNotFound
    XMLParsingError = XMLParsingError
    InvalidCredentialsError = InvalidCredentialsError
    SchulnummerNotFoundError = SchulnummerNotFoundError


