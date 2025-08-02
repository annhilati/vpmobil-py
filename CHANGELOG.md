## [1.0.0](https://pypi.org/project/vpmobil/1.0.0/) (2025-08)

### 🔧 Änderungen

* Neustrukturierung der gesammten Kernfunktionalität durch die Verwendung modernerer Syntax
* Die Werkzeugklasse `workflow` wurde aufgelöst. Alle Klassen, Funktionen und Exceptions können einfach aus `vpmobil` importiert werden
* Die meisten Funktionen und Eigenschaften gegeben nun `None` zurück statt einen Fehler zu werfen, wenn in dem XML-Daten nicht gefunden wird

### 🪲 Bug Fixes

* In der Nachricht des `FetchingError`s, der bei `Vertretungsplan.fetch()` geworfen wird, wird die Datei, die nicht abgerufen werden konnte, nicht richtig benannt. 

## [0.4.2](https://pypi.org/project/vpmobil/0.4.2/) (2024-12-28)

### 🔧 Änderungen

* Werkzeugsammlungsklasse von `vpmobil.VpMobil` in `vpmobil.workflow` umbenannt