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
from .parser import VpDay, Klasse, Stunde, Kurs
from .io import parsefromfile
from .exceptions import FetchingError, InvalidCredentialsError, XMLParsingError

_symbols = [Vertretungsplan,
            VpDay, Klasse, Stunde, Kurs,
            parsefromfile,
            FetchingError, InvalidCredentialsError, XMLParsingError]
_constants = []

__all__ = [obj.__name__ for obj in _symbols].extend(_constants)