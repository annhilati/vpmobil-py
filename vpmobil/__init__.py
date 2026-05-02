"""
API wrapper module for interacting with vpmobil substitution plans

[[Repository]](https://github.com/annhilati/vpmobil-py)
[[Documentation]](https://annhilati.github.io/vpmobil-py/)
```
"""

from vpmobil.api import VertretungsplanZugang, VpMobilPyError, Unauthorized, ResourceNotFound, Standardpfade
from vpmobil.models import (
    Vertretungsplan,
    Klasse, Raum, Lehrer,
    Stunde, Kurs, Aufsicht, Klausur
    )
from vpmobil.parser import Parser

_symbols = [
    VertretungsplanZugang,
    Vertretungsplan,
    Klasse, Lehrer, Raum,
    Stunde, Kurs, Aufsicht, Klausur,
    VpMobilPyError, Unauthorized, ResourceNotFound,
    Standardpfade, Parser
]
_constants = []

__all__ = [obj.__name__ for obj in _symbols] + _constants