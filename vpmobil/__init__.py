"""
API wrapper module for interacting with vpmobil substitution plans

---

**💡 Wie man beginnt**
```python
from vpmobil import Vertretungsplan
vp = Vertretungsplan(10323955, "schueler", "h39gh23")
heute = vp.fetch()
```

---

📦 Alle relevanten Klassen können direkt aus `vpmobil` importiert werden.

---

⚙️ Konfiguration kann im `config`-Submodul vorgenommen werden.

---

🛠️ Im `extensions`-Submodul befinden sich weitere Indiware-related Funktionen.
"""

from vpmobil.api import Vertretungsplan, IndiwareFetchingError, Unauthorized, ResourceNotFound, Stundenplan24Pfade
from vpmobil.models import (
    KlassenVertretungsTag, LehrerVertretungsTag, RaumVertretungsTag,
    Klasse, Raum, Lehrer,
    Stunde, Kurs, Aufsicht
    )
_symbols = [
    Vertretungsplan,
    KlassenVertretungsTag, LehrerVertretungsTag, RaumVertretungsTag,
    Klasse, Lehrer, Raum,
    Stunde, Kurs, Aufsicht,
    IndiwareFetchingError, Unauthorized, ResourceNotFound,
    Stundenplan24Pfade
]
_constants = []

__all__ = [obj.__name__ for obj in _symbols] + _constants