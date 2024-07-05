# Vertretungsplandaten abrufen

```python
from vpmobil import Vertretungsplan

plan = Vertretungsplan(10323955, "schueler", "h39gh23")
# Deklariere eine Vertretungsplan-Instanz

heute = plan.fetch()
# Erstelle ein VpDay-Objekt, dass die heutigen Daten enthält

xml = heute.getxml() # Erhalte die gesammten Daten als XML ElementTree
string = heute.getxml("str") # Erhalte die gesammten Daten als Zeichenkette
```
