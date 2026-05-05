---
title: Getting Started
icon: lucide/arrow-down-to-line
---

# Getting Started

## 1. Stundendaten auswerten

```python
from vpmobil import VertretungsplanZugang

plan = VertretungsplanZugang(10000000, "schueler", "password")
# Eine VertretungsplanZugang-Instanz erstellen

heute = plan.get()
# Die heutigen Plandaten abrufen

klasse8b = heute.klassen["8b"]
# Eine Klasse isolieren

for periode, stunden in klasse8b.stunden:
    for stunde in stunden:
        print(f"{periode} | {stunde.fach} bei {stunde.lehrer}")
# Details zu den Stunden der Klasse ausgeben
```

## 2. Andere Pläne abrufen

```python
from vpmobil import VertretungsplanZugang, Standardpfade, Unauthorized
from datetime import date

plan = VertretungsplanZugang(10000000, "schueler", "password")

try:
    tag = plan.get(date(2025, 10, 5), datei=Standardpfade.PlanRa)
    # Die Plandaten der Räume vom 5.10.2025 abrufen

except Unauthorized:
    # Abfangen, falls die Zugangsdaten keine Berechtigung für Raumpläne haben
    continue
...
```

## 3. Pläne aus anderen Perspektiven auswerten

```python
from vpmobil import VertretungsplanZugang, Standardpfade

plan = VertretungsplanZugang(10000000, "schueler", "password")
heute = plan.get(datei=Standardpfade.PlanKl)
# Den heutigen Klassenplan abrufen

for lehrer in heute.lehrer:
    print(lehrer)
# Details zu den Lehrern ausgeben
```
