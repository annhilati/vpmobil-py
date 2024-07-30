"""
A python wrapper package for interacting with a stundenplan24.de substitution plan
"""

from .fetcher import Vertretungsplan
from .parser import VpDay, Klasse, Stunde, getxml
from .workflow import Exceptions

__all__ = ['VpMobil', 'Vertretungsplan', 'VpDay', 'Klasse', 'Stunde']
    # Enthält alle Symbole, die bei "from vpmobil import" verfügbar sind
    # Enthält alle Symbole, die bei "from vpmobil import *" importiert werden

class VpMobil:
    """
    Enthält nützliche Funktionen für den Arbeitsablauf

    #### Funktionen
        getxml(): Isoliert die XML-Datenobjekte eines VpMobil-Objekts

    #### Exceptions
        FetchingError: Wenn Daten nicht abgerufen werden können
        XMLParsingError: Wenn XML-Daten nicht richtig ausgewertet werden können
            XMLNotFound: Wenn ein Element der XML-Daten nicht gefunden werden kann
    """

    getxml = getxml
    """
    Gibt die XML Daten eines Objekts als Klasse des xml-Moduls zurück

    #### Argumente
        object (VpDay | Klasse | Stunde): Vertretungsplan-Objekt, aus dem die XML-Daten isoliert werden sollen

    #### Returns
        ElementTree: Wenn object einen VpDay-Objekt ist
        Element: Wenn object einen Klassen-Objekt ist
        Element: Wenn object einen Stunden-Objekt ist
    """
    
    FetchingError = Exceptions.FetchingError
    XMLNotFound = Exceptions.XMLNotFound
    XMLParsingError = Exceptions.XMLParsingError

