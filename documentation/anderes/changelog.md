# Changelog

### Development

#### 🚀 Neue Funktionen

* Datenmodelle können nun mit `._to_dict()` in Dictionaries umgewandelt werden<br>
    > Dies ist ersteinmal eine Übergangslösung, um das Speichern in gut les- und parsbaren Formaten zu ermöglichen. Das Format wird sich in Zukunft sicherlich nochmals ändern.
* `Vertretungsplan()` hat nun einen neuen Parameter `Port` (int). Mit ihm kann der Port des Service übergeben werden, über den die Vertretungsplandaten bereitstellt werden

#### 🔧 Änderungen

* `Stunde.lehrer` gibt die Lehrer der Stunde nun als Liste von Strings zurück. Statt `None` wird `[]` zurückgegeben
* `Stunde.raum` wurde entfernt
* `Stunde.räume` gibt nun die Räume der Stunde als Liste von Strings zurück. Statt `None` wird `[]` zurückgegeben
* Die Option, mit `Vertretungsplan.fetch()` über den Parameter `datei` eine bestimmte Datei abzurufen wurde vorerst entfernt
* `Klasse.stundenHeuteInPeriode()` gibt nun `[]` statt `None` zurück, wenn keine Stunden vorhanden sind

#### 🪲 Bug Fixes

* `VertretungsTag.lehrerKrank` wirft einen Fehler, wenn es einen Kurs gibt, der keinen Lehrer hat

### [1.1.0](https://pypi.org/project/vpmobil/1.1.0/) (2025-08-27)

#### 🚀 Neue Funktionen

* Weitere Funktionalität zum verarbeiten von von Indiware-Software bereitgestellter Daten ist nun im Submodul `extensions` verfügbar
* Kurse und deren Schüler einer Klasse können nun mit `vpmobil.extensions.einzpläne.kurse()` aus EinzPläne-PDF-Dateien gelesen werden
* Tutoren und deren Schüler einer Klasse können nun mit `vpmobil.extensions.einzpläne.tutoren()` aus EinzPläne-PDF-Dateien gelesen werden

#### 🔧 Änderungen

* `VpDay` wurde in `VertretungsTag` umbenannt
* `vpmobil.parsefromfile()` wurde nach `vpmobil.VertretungsTag.fromfile()` verschoben und kann nun nicht mehr direkt importiert werden
* Das Projekt ist nun unter _European Union Public License 1.2_ lizensiert
* Ein paar Docstrings wurden konkretisiert oder weisen nun auf mögliche Inkonsistenzen hin
* `Vertretungsplan.fetchall()` wurde in `Vertretungsplan.bulkfetch()` umbenannt

#### 🪲 Bug Fixes

* `Vertretungsplan.fetchall()` raised nicht `ResourceNotFound` sondern `IndiwareFetchingError`, wenn keine Pläne gefunden wurden

### [1.0.1](https://pypi.org/project/vpmobil/1.0.1/) (2025-08-03)

#### 🪲 Bug Fixes

* `from vpmobil import *` importiert nichts

### [1.0.0](https://pypi.org/project/vpmobil/1.0.0/) (2025-08-03)

#### 🚀 Neue Funktionen

* Ein bestimmter Kurs kann per Kursnummer mit `Klasse.kurs()` erhalten werden

#### 🔧 Änderungen

* Neustrukturierung der gesammten Kernfunktionalität durch die Verwendung modernerer Syntax
* Die Werkzeugklasse `workflow` wurde aufgelöst. Alle Klassen, Funktionen und Exceptions können einfach aus `vpmobil` importiert werden
* Die meisten Funktionen und Eigenschaften gegeben nun `None` zurück statt einen Fehler zu werfen, wenn in den XML-Daten nichts gefunden wird
* Einige unhandliche und unnötige Methoden von `Klasse` wurden entfernt
* Ein paar Exceptions wurden umbenannt, entfernt oder durch built-ins ersetzt
* Einige Module wurden zusammengeführt und umbenannt

#### 🪲 Bug Fixes

* In der Nachricht des `FetchingError`s, der bei `Vertretungsplan.fetch()` geworfen wird, wird die Datei, die nicht abgerufen werden konnte, nicht richtig benannt

#### ⚠️ Bekannte Probleme

* `VpDay.lehrerKrank` behandelt mehrere in einem Kurs oder einer Stunde angeführte Lehrer nicht mehr separat

### [0.4.2](https://pypi.org/project/vpmobil/0.4.2/) (2024-12-28)

#### 🔧 Änderungen

* Werkzeugsammlungsklasse von `vpmobil.VpMobil` in `vpmobil.workflow` umbenannt
