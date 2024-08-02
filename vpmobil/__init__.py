"""
A python wrapper package for interacting with a stundenplan24.de substitution plan

    >>> from vpmobil import Vertretungsplan
    >>> vp = Vertretungsplan(39563772, "schueler", "j39jjs6")
    >>> tag = vp.fetch(20240619)
    >>> klasse = tag.klasse("9b")
    >>> stunden = klasse.stunden()
    >>> for stunde in stunden:
    >>>     print(f"{stunde.nr}: {stunde.fach} bei {stunde.lehrer} in {stunde.raum}")
"""

from .fetcher import Vertretungsplan
from .parser import VpDay, Klasse, Stunde

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
            - InvalidCredentialsError: Wenn die angegebene Anmeldedaten ungültig sind
            - SchulnummerNotFoundError: Wenn die angegebene Schulnummer nicht registriert ist
        XMLParsingError: Wenn XML-Daten nicht richtig ausgewertet werden können
            - XMLNotFound: Wenn ein Element der XML-Daten nicht gefunden werden kann
    """

    from .io import getxml, parsefromfile
    getxml = getxml
    parsefromfile = parsefromfile
    
    from .exceptions import Exceptions
    FetchingError = Exceptions.FetchingError
    XMLNotFound = Exceptions.XMLNotFound
    XMLParsingError = Exceptions.XMLParsingError
    InvalidCredentialsError = Exceptions.InvalidCredentialsError
    SchulnummerNotFoundError = Exceptions.SchulnummerNotFoundError


