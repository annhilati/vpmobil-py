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
from .io import getxml, parsefromfile
from .exceptions import FetchingError, InvalidCredentialsError, XMLParsingError, XMLNotFound

_symbols = [Vertretungsplan,
            VpDay,
            Klasse, Stunde,
            getxml,
            parsefromfile,
            FetchingError, InvalidCredentialsError, XMLParsingError, XMLNotFound]
_constants = []

__all__ = [obj.__name__ for obj in _symbols].extend(_constants)