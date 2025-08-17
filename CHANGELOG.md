## Development

### 🚀 Neue Funktionen

* Weitere Funktionalität zum verarbeiten von von Indiware-Software bereitgestellter Daten ist nun im Submodul `extensions` verfügbar
* Kurse und deren Schüler einer Klasse können nun mit `vpmobil.extensions.einzpläne.kurse()` aus EinzPläne-PDF-Dateien gelesen werden 
* Tutoren und deren Schüler einer Klasse können nun mit `vpmobil.extensions.einzpläne.tutoren()` aus EinzPläne-PDF-Dateien gelesen werden 
* `Kurs`e und `Stunde`n können jetzt auf Gleichheit verglichen werden

### 🔧 Änderungen

* `VpDay` wurde in `VertretungsTag` umbenannt
* Das Projekt ist nun unter *European Union Public License 1.2* lizensiert
* Ein paar Docstrings wurden konkretisiert oder weisen nun auf mögliche Inkonsistenzen hin
* `vpmobil.parsefromfile()` wurde nach `vpmobil.extensions.io.parsefromfile()` verschoben und kann nun nicht mehr direkt importiert werden

### 🪲 Bug Fixes

* `Vertretungsplan.fetchall()` raised nicht `ResourceNotFound` sondern `IndiwareFetchingError`, wenn keine Pläne gefunden wurden

## [1.0.1](https://pypi.org/project/vpmobil/1.0.1/) (2025-08-03)

### 🪲 Bug Fixes

* `from vpmobil import *` importiert nichts

## [1.0.0](https://pypi.org/project/vpmobil/1.0.0/) (2025-08-03)

### 🚀 Neue Funktionen

* Ein bestimmter Kurs kann per Kursnummer mit `Klasse.kurs()` erhalten werden

### 🔧 Änderungen

* Neustrukturierung der gesammten Kernfunktionalität durch die Verwendung modernerer Syntax
* Die Werkzeugklasse `workflow` wurde aufgelöst. Alle Klassen, Funktionen und Exceptions können einfach aus `vpmobil` importiert werden
* Die meisten Funktionen und Eigenschaften gegeben nun `None` zurück statt einen Fehler zu werfen, wenn in den XML-Daten nichts gefunden wird
* Einige unhandliche und unnötige Methoden von `Klasse` wurden entfernt
* Ein paar Exceptions wurden umbenannt, entfernt oder durch built-ins ersetzt
* Einige Module wurden zusammengeführt und umbenannt

### 🪲 Bug Fixes

* In der Nachricht des `FetchingError`s, der bei `Vertretungsplan.fetch()` geworfen wird, wird die Datei, die nicht abgerufen werden konnte, nicht richtig benannt

### ⚠️ Bekannte Probleme

* `VpDay.lehrerKrank` behandelt mehrere in einem Kurs oder einer Stunde angeführte Lehrer nicht mehr separat

## [0.4.2](https://pypi.org/project/vpmobil/0.4.2/) (2024-12-28)

### 🔧 Änderungen

* Werkzeugsammlungsklasse von `vpmobil.VpMobil` in `vpmobil.workflow` umbenannt