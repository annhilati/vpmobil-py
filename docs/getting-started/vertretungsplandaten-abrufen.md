---
title: Vertretungspläne abrufen
icon: lucide/arrow-down-to-line
---

# Vertretungsplandaten abrufen

## 1. Stundendaten auswerten

```python
from vpmobil import Vertretungsplan

plan = Vertretungsplan(10000000, "schueler", "password")
# Eine Vertretungsplan-Instanz erstellen

heute = plan.fetch()
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
from vpmobil import Vertretungsplan, Stundenplan24Pfade, Unauthorized
from datetime import date

plan = Vertretungsplan(10000000, "schueler", "password")

try:
    tag = plan.fetch(date(2025, 10, 5), datei=Stundenplan24Pfade.PlanRa)
    # Die Plandaten der Räume vom 5.10.2025 abrufen

except Unauthorized:
    # Abfangen, falls die Zugangsdaten keine Berechtigung für Raumpläne haben
    continue

...
```

## 3. Pläne aus anderen Perspektiven auswerten

```python
from vpmobil import Vertretungsplan, Stundenplan24Pfade
from vpmobil.extensions.reparser import LehrerPerspektive

plan = Vertretungsplan(10000000, "schueler", "password")
heute = plan.fetch(datei=Stundenplan24Pfade.PlanKl)
# Den heutigen Klassenplan abrufen

reparsed = LehrerPerspektive(heute)
# Klassenplan in einen Lehrerplan umwandeln

for lehrer in reparsed.lehrer:
    print(lehrer)
# Details zu den Lehrern ausgeben
```
