# Vertretungsplandaten abrufen

```python
from vpmobil import Vertretungsplan

plan = Vertretungsplan(10323955, "schueler", "h39gh23")
# Deklariere eine Vertretungsplan-Instanz

heute = plan.fetch()
# Erstelle ein VpDay-Objekt, dass die heutigen Daten enthält

klasse8b = heute.klasse("8b")

for periode, stunden in klasse8b.stundenHeute:
    for stunde in stunden:
        print(f"{periode} | {stunde.fach} bei {stunde.lehrer}")
# Listet die Stunden der Klasse 8b in der Konsole auf
```
