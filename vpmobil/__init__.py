"""
Python API wrapper library for evaluating VpMobil substitution plans

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


__all__ = [
    "VertretungsplanZugang",
    "Vertretungsplan",
    "Klasse", "Lehrer", "Raum",
    "Stunde", "Kurs", "Aufsicht", "Klausur",
    "VpMobilPyError", "Unauthorized", "ResourceNotFound",
    "Standardpfade", "Parser"
]