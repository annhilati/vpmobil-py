"""
API wrapper module for interacting with vpmobil substitution plans

---

**💡 Wie man beginnt**
```python
from vpmobil import Vertretungsplan
vp = Vertretungsplan(10000000, "schueler", "password")
heute = vp.fetch()
```

---

📦 Alle grundlegenden Klassen können direkt aus `vpmobil` importiert werden.

---

⚙️ Konfiguration kann im `config`-Submodul vorgenommen werden.

---

🛠️ Im `extensions`-Submodul befinden sich weitere Indiware-related Funktionen.
```
└── extensions
    ├── einzpläne        # Funktionen zum auswerten von EinzPläne-PDFs
    └── reparser         # Funktionen zum ändern der Perspektive eines VertretungsTags
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
    Standardpfade
]
_constants = []

__all__ = [obj.__name__ for obj in _symbols] + _constants