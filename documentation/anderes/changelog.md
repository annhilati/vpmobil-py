# Changelog

## [2.0.0](https://pypi.org/project/vpmobil/2.0.0/) (2025-10-??)

### 🚀 Neue Funktionen

* Vollumfänglicher Support für Lehrer- und Raumpläne hinzugefügt
* Parameter `port` zu `Vertretungsplan` hinzugefügt
* Enumerator `Stundenplan24Pfade` hinzugefügt, der die Standardpfade auf stundenplan24.de enthält
* Submodul `config` hinzugefügt, das Parameter für das Parsing enthält
* Datenmodelle können mit `._as_dict()` in ein sauberes JSON-kompatibles Dictionary umgewandelt werden<br>
  > Diese Implementierung ist noch experimentell und kann sich in Zukunft ändern.

#### Lehrer- & Raumpläne

Im Rahmen der Einführung neuer Vertretungsplantypen wurden einige Datenmodelle in Basis- und Unterklassen aufgeteilt.
Die drei Vertretungsplanklassen `VertretungsTag`, `LehrerVertretungsTag` und `RaumVertretungsTag` erben von einer neuen Basisklasse, die grundlegendes Verhalten für Pläne enthält. Die einzelnen Planklassen bringen dann noch weitere Funktionen mit.

Neue Klassen sind:

* `MobdatenBase`
  * Basisklasse für Vertretungspläne
  * Erzeugt beim Instanzierungsversuch eine Instanz einer ihrer Subklassen
  * Kann mit `isinstance()` als Protokoll für alle Vertretungspläne genutzt werden
  * Kann vererbt werden, um weitere Planarten zu definieren 
* `LehrerVertretungsTag`
  * Subklasse von `MobdatenBase`
  * Hat `.lehrer` und `.get_lehrer()`
* `RaumVertretungsTag`
  * Subklasse von `MobdatenBase`
  * Hat `.räume` und `.raum()`
* `Lehrer`
  * Das Lehrerplan-Äquivalent zu `Klasse`
  * Wird von `LehrerVertretungsTag.lehrer` erzeugt
* `Raum`
  * Das Raumplan-Äquivalent zu `Klasse`
  * Wird von `RaumVertretungsTag.räume` erzeugt
* `Aufsicht`
  * Ein primitives Datenmodell, ähnlich zu `Stunde`, das Informationen über eine Lehreraufsicht enthält
  * Hat `.vorStunde`, `.uhrzeit`, `.zeit` und `.ort`
  * Wird von `Lehrer.aufsichten` erzeugt

### 🔧 Änderungen

* `Vertretungsplan` und `.fetch()` wurden angepasst, um die neuen Vertretungsplanarten verarbeiten zu können
* `Stunde.raum` wurde durch `Stunde.räume` ersetzt, das nun eine Liste von Strings zurückgibt. Statt `None` wird `[]` zurückgegeben
* `Stunde.lehrer` gibt nun eine Liste von Strings zurück. Statt `None` wird `[]` zurückgegeben
* `Klasse.stundenHeuteInPeriode()` gibt nun `[]` statt `None` zurück
* Alle Properties, die Klassen, Lehrer oder Räume zurückgeben, verwenden nun das Trennzeichen, das in `config.SEPARATOR` festgelegt werden kann, um Mehrfachnennungen zu trennen
* Alle Properties wurden `None`-sicher gemacht, sodass sie nun keine Fehler mehr werfen können, sollte ein Tag in der Quelldatei unerwarteter Weise nicht vorhanden sein
* `InvalidCredentialsError` wurde in `Unauthorized` umbenannt
* `Vertretungsplan.bulkfetch()` wurde entfernt
* `Kurs.gruppe` wurde in `.kürzel` umbenannt. Es gibt jetzt als Fallback `.fach` zurück
* `Klasse.stundenHeute` wurde in `.stunden` und `.stundenHeuteInPeriode` in `.stundenInPeriode` umbenannt
* `VertretungsTag.freieTage` gibt statt `None` nun `[]` zurück

#### `Vertretungsplan` und `.fetch()`
`Vertretungsplan` ist nun so konzipiert, dass es ein Standardpfadschema für Dateiabrufe gibt. Andere Dateien können in `.fetch()` dennoch weiterhin abgerufen werden. 

* Parameter `vezeichnis` und `dateinamenschema` von `.fetch()` wurden in `dateipfadschema` zusammengeführt
* Wenn `.fetch()` mit dem Parameter `datei` angegeben wird, ersetzt das den Standarddateipfad. `datei` kann, wie `Vertretungsplan.dateipfadschema` mit Platzhaltern des datetime-Moduls und dem Platzhalter `schulnummer` verwendet werden

### 🪲 Bug Fixes

* `VertretungsTag.lehrerKrank` wirft einen Fehler, wenn es einen Kurs gibt, der keinen Lehrer hat



## [1.1.0](https://pypi.org/project/vpmobil/1.1.0/) (2025-08-27)

### 🚀 Neue Funktionen

* Weitere Funktionalität zum verarbeiten von von Indiware-Software bereitgestellter Daten ist nun im Submodul `extensions` verfügbar
* Kurse und deren Schüler einer Klasse können nun mit `vpmobil.extensions.einzpläne.kurse()` aus EinzPläne-PDF-Dateien gelesen werden
* Tutoren und deren Schüler einer Klasse können nun mit `vpmobil.extensions.einzpläne.tutoren()` aus EinzPläne-PDF-Dateien gelesen werden

### 🔧 Änderungen

* `VpDay` wurde in `VertretungsTag` umbenannt
* `vpmobil.parsefromfile()` wurde nach `vpmobil.VertretungsTag.fromfile()` verschoben und kann nun nicht mehr direkt importiert werden
* Das Projekt ist nun unter _European Union Public License 1.2_ lizensiert
* Ein paar Docstrings wurden konkretisiert oder weisen nun auf mögliche Inkonsistenzen hin
* `Vertretungsplan.fetchall()` wurde in `Vertretungsplan.bulkfetch()` umbenannt

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
