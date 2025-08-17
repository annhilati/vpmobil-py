"""
API wrapper module for interacting with vpmobil substitution plans

---

### Beispiel für die Nutzung
```python
from vpmobil import Vertretungsplan
plan = Vertretungsplan(10323955, "schueler", "h39gh23")
heute = plan.fetch()
klasse8b = heute.klasse("8b")
for periode, stunden in klasse8b.stundenHeute:
    for stunde in stunden:
        print(f"{periode} | {stunde.fach} bei {stunde.lehrer}")
```

---

Siehe auch das `extensions`-Submodul. Importe aus anderen Submodulen sind in der Regel nicht notwendig.
"""

from vpmobil.api import Vertretungsplan, IndiwareFetchingError, InvalidCredentialsError, ResourceNotFound
from vpmobil.models import VertretungsTag, Klasse, Stunde, Kurs

_symbols = [Vertretungsplan,
            VertretungsTag, Klasse, Stunde, Kurs,
            IndiwareFetchingError, InvalidCredentialsError, ResourceNotFound]
_constants = []

__all__ = [obj.__name__ for obj in _symbols] + _constants