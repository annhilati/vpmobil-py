"""
A python wrapper package for interacting with stundenplan24.de substitution plans

```
from vpmobil import Vertretungsplan
plan = Vertretungsplan(10323955, "schueler", "h39gh23")
heute = plan.fetch()
klasse8b = heute.klasse("8b")
for periode, stunden in klasse8b.stundenHeute:
    for stunde in stunden:
        print(f"{periode} | {stunde.fach} bei {stunde.lehrer}")
```
"""

from .io import parsefromfile
from .api import Vertretungsplan, IndiwareFetchingError, InvalidCredentialsError, ResourceNotFound
from .models import VpDay, Klasse, Stunde, Kurs

_symbols = [Vertretungsplan,
            VpDay, Klasse, Stunde, Kurs,
            parsefromfile,
            IndiwareFetchingError, InvalidCredentialsError, ResourceNotFound]
_constants = []

__all__ = [obj.__name__ for obj in _symbols] + _constants