---
icon: lucide/scroll-text
---

# Changelog

## [3.1.0](https://pypi.org/project/vpmobil/3.1.0/) (2026-09-XX)

### 🚀 Neuerungen

- Einführung der `Repository[T]`-Architektur für Listen-Attribute wie `klassen`, `lehrer` und `räume` in Modellen, um Redundanzen beim Mergen automatisch zu vermeiden und eine saubere Mutierbarkeit bei gleichzeitiger Sortierung zu gewährleisten
- Implementierung von dynamischen Views (`SelectionProxy`, `GroupedSelectionProxy`) für abgeleitete Modelleigenschaften, die sich automatisch mit dem `Vertretungsplan` synchronisieren
- Feld `parser` zu `VertretungsplanZugang` hinzugefügt. `VertretungsplanZugang.get()` übernimmt dessen Wert standardmäßig für den Parameter `parser`

### 🔧 Änderungen

- Methode `Vertretungsplan.saveasfile()` in `~.export()` umbenannt
- Die Export-Methodik via `Vertretungsplan.export()` (insbesondere bei YAML-Dateien) übernimmt nun durchgehend die natürliche Sortierung von Kürzeln, um die Navigierbarkeit zu verbessern
- Feld `Klausur.lehrer` hat nun den Typ `Repository[str]` statt `str | None`
- Methode `VertretungsplanZugang.get()` kann nun sowohl mit `date` als auch mit `str` als Positionsargument genutzt werden. Das jeweils andere oder auch beide können weiterhin als Keyword-Argumente übergeben werden

### 🪲 Fehlerbehebungen

- Behebung eines Fehlers, bei dem das Standard-Datum in `VertretungsplanZugang.get()` nur einmal beim Import der Bibliothek ausgewertet wurde und bei längerer Laufzeit veraltete. Das Datum wird nun zur Laufzeit ausgewertet.

## [3.0.2](https://pypi.org/project/vpmobil/3.0.2/) (2026-07-02)
### 🔧 Änderungen

- `~.stunden` von `Klasse`, `Lehrer` und `Raum` werden nun korrekt nach Unterrichtsperiode sortiert
- Paket `pdfplumber` ist nun keine strenge Voraussetzung mehr, um Geräte ohne C++-Distribution nicht einzuschränken. Es kann durch Angabe des Installationsparameters `pdfs` wie in `pip install vpmobil[pdfs]` mitinstalliert werden
- Formatierungssicherheit der Darstellungen von `Vertretungsplan`-, `Stunde`-, `Kurs`-, `Aufsicht`- und `Klausur`-Objekten verbessert
- `Stunde`, `Kurs`, `Aufsicht`, `Klausur` speichern `klassen`, `lehrer`, `räume` und `kurse` nun als `tuple[str, ...]` anstatt als `set[str]`, um die Sortierung der Kürzel beizubehalten
- Kürzel von Klassen, Lehrern und Räumen in Stunden, Kursen, Aufsichten, Klausuren, `freieRäume` und `abwesendeLehrer` werden nun natürlich sortiert (z.B. "5a" vor "10a")
  
### 🪲 Fehlerbehebungen

- Parameter `parser` von `Vertretungsplan.fromfile()` erhält als Standardwert `Parser`, nicht aber `Parser()`
- Die Erweiterungsmodule `exensions.~` fehlen
- Behebung eines Fehlers (`TypeError: mappingproxy() argument must be a mapping, not list`), der auftrat, wenn die generierten Eigenschaften `~.stunden` von `Klasse`, `Lehrer` und `Raum` aufgerufen wurden
- Behebung einer Endlosschleife bzw. falscher Zuordnung beim Auswerten von Klausuren für die Eigenschaft `Vertretungsplan.klassen`
- Behebung der verschachtelten Methodendefinition von `VpMobilPyModell.__copy__`, die immer `None` zurückgab


## [3.0.1](https://pypi.org/project/vpmobil/3.0.1/) (2026-05-05)

### 🔧 Änderungen

- Parsing von `~.datum` in `Vertretungsplan.from_xml()` weniger anfällig für Lokalitätsprobleme gemacht


## [3.0.0](https://pypi.org/project/vpmobil/3.0.0/) (2026-05-05)

!!! warning
    Diese Version enthält viele weitere Änderungen, die hier nicht alle aufgelistet werden können. Es wird empfohlen, sich Zeit zu nehmen, alte Programme mit der neuen Version durchzutesten und da Anpassungen vorzunehmen, wo sie benötigt werden. Die Docstrings der geänderten Funktionen sind ziemlich umfangreichlich und sollten bei der Umstellung helfen.

### 🚀 Neuerungen

!!! question
    Einige Namen haben sich geändert. Es ist zu empfehlen, zuvor den Abschnitt *Umbenennungen* zu lesen.

<!-- 
    Zuerst benennen wir alle Neuerungen, ohne zu sehr ins Detail zu gehen.
    Es ist in Ordnung den konkreten Sinn zu beschreiben, falls es unklar sein könnte 
    
    - Mit "hinzugefügt" enden
-->
- Klarwert-Konstruktoren für `Vertretungsplan`, `Stunde`, `Klausur`, `Aufsicht`, `Klasse`, `Lehrer` und `Raum` hinzugefügt
- Kompatibilität für `copy` und `deepcopy` aus dem `copy`-Modul für `Vertretungsplan`, `Stunde`, `Klausur`, `Aufsicht`, `Klasse`, `Lehrer` und `Raum` hinzugefügt
- Methode `~.copy` für `Vertretungsplan`, `Stunde`, `Klausur`, `Aufsicht`, `Klasse`, `Lehrer` und `Raum` hinzugefügt
- Methode `~.to_xml()` für `Vertretungsplan`, `Stunde`, `Klausur`, `Aufsicht`, `Klasse`, `Lehrer` und `Raum` hinzugefügt
- Methode `VertretungsplanZugang.getall()` hinzugefügt
- Eigenschaft `Vertretungsplan.zeitplan` hinzugefügt
- Methode `Vertretungsplan.saveasfile()` hinzugefügt
- Feld `Stunde.fachmeta` hinzugefügt, das die Information aus dem `Ku2`-Tag der Quelldaten abbildet
- Modul `extensions.parser_presets` (und Alias `~.pp`) hinzugefügt
- Klasse `Parser` hinzugefügt, die nun anstatt des Modul `config` Parameter für das Parsing enthält

<!-- Einzelne Features könnte man hier nochmal genauer erläutern -->

### 🏷️ Namensänderungen
<!-- Schon in einem Punkt benannte Symbole können mit ~ referenziert werden -->
- `Vertretungsplan` in `VertretungsplanZugang` umbenannt
- `VertretungsplanZugang.serverdomain` in `~.domain` umbenannt
- `VertretungsplanZugang.fetch()` in `~.get()` umbenannt
- `Stundenplan24Pfade` in `Standardpfade` umbenannt
- `Vertretungsplan.saveasfile()` in `~.save_xml` umbenannt
- `Vertretungsplan.datei` in `~.dateiname` umbenannt
- `Vertretungsplan.lehrerKrank` in `abwesendeLehrer` umbenannt
- `KlassenVertretungsTag`, `LehrerVertretungsTag` und `RaumVertretungsTag` finden sich als `Vertretungsplan`-Klasse wieder (siehe *Änderungen*)

### 🗑️ Entfernungen
- `extensions.config_presets` entfernt (durch `parser_presets` ersetzt)
- `~.stundenInPeriode()` von `Klasse`, `Lehrer` und `Raum` entfernt

### 🔧 Änderungen

- `Vertretungsplan`, `Stunde`, `Klausur`, `Aufsicht`, `Klasse`, `Lehrer` und `Raum` speichern Daten nicht mehr als XML-`Element`, sondern in Klarwerten, beziehungsweise Instanzen der jeweils anderen Klassen
    - Ihre Konstruktoren nehmen kein `Element` mehr entgegen. Instantiierung aus `Element`-Objekten kann mit `~.from_xml()` vorgenommen werden
- Vertretungspläne jeder Art werden nur noch durch die `Vertretungsplan`-Klasse abgebildet
- `Klasse`, `Raum` und `Lehrer` sind nur noch Proxies, die bis auf das Kürzel nur immutable Objekte mit Referenzen auf Objekte in den Feldern von `Vertretungsplan` enthalten
- `Vertretungsplan.abwesendeLehrer` gibt nicht nur die Kürzel aller Lehrer zurück, die unplanmäßig keinen Unterricht haben, sondern die aller Lehrer, die keine Stunden haben
- `Stunde.lehrergeändert`, `~.raumgeändert` und `.~klassegeändert` können beim entsprechenden Plantypen nun nicht mehr `None` sein. Stattdessen wird `~.geändert` weitergegeben
- Das Typing der Felder von `Klasse`, `Raum` und `Lehrer` enthält nun oft `Mapping`, stehend für eine `MappingProxyType`-Instanz und `Collection`, stehend für eine Tupel
- Alle Docstrings wurden überarbeitet
- Das Modul `extensions.einzpläne` und seine Funktionen verwenden nun die Bibliothek `pdfplumber` an Stelle von `PyPDF2`


## [2.1.0.1](https://pypi.org/project/vpmobil/2.1.0.1/) (2026-03-27)

### 🪲 Bug Fixes
* Auf manchen Maschinen wird ein Fehler geworfen, weil `Stunde.__repr__` eine Quote-Kollision hat

## [2.1.0](https://pypi.org/project/vpmobil/2.1.0/) (2026-03-27)

### 🚀 Neue Funktionen

* Funktion `VertretungsTag.freieRäume()` zum Finden in einem bestimmten Zeitraum freier Räume

### 🔧 Änderungen

* `IndiwareFetchingError` wurde in `VpMobilPyError` umbenannt
* `config.set_config` kann nun auch Keyword-Argumente entgegennehmen
* Typing für Funktionen in der `reparser`-Extension wurde verallgemeinert

### 🪲 Bug Fixes

* Regex-Muster in Presets werden fälschlicherweise kompilliert
* Das Dekodieren von Zeitstrings funktioniert auf manchen Geräten nicht
* Syntax im Tip von `Stunde.fach` korrigiert
* Typ-Annotation von `Klasse.kurse` korrigiert
* Auf manchen Maschinen wird ein Fehler geworfen, weil `VertretungsTag.__new__` eine Quote-Kollision hat

## [2.0.0](https://pypi.org/project/vpmobil/2.0.0/) (2025-11-10)

### 🚀 Neue Funktionen

* Vollumfänglicher Support für Lehrer- und Raumpläne hinzugefügt, Support für Klassenpläne vervollständigt
* Parameter `port` zu `Vertretungsplan` hinzugefügt
* Enumerator `Stundenplan24Pfade` hinzugefügt, der die Standardpfade auf stundenplan24.de enthält
* Submodul `config` hinzugefügt, das Parameter für das Parsing enthält
* Datenmodelle können mit `.as_dict()` in ein sauberes JSON-kompatibles Dictionary umgewandelt werden<br>
* Konversionsfunktionen zwischen `VertretungsTag`-Datenmodellen in `extensions.reparser` hinzugefügt

#### Lehrer- & Raumpläne

Im Rahmen der Einführung neuer Vertretungsplantypen wurden einige Datenmodelle in Basis- und Unterklassen aufgeteilt. Die drei Vertretungsplanklassen `KlassenVertretungsTag`, `LehrerVertretungsTag` und `RaumVertretungsTag` erben von einer neuen Basisklasse, die grundlegendes Verhalten für Pläne enthält. Die einzelnen Planklassen bringen dann noch weitere Funktionen mit.

Neue Klassen sind:

* `VertretungsTag`
    * Basisklasse für Vertretungspläne
    * Erzeugt beim Instanzierungsversuch eine Instanz einer ihrer Subklassen
    * Kann mit `isinstance()` als Protokoll für alle Vertretungspläne genutzt werden
* `LehrerVertretungsTag`
    * Subklasse von `VertretungsTag`
    * Hat `.lehrer` und `.get_lehrer()`
* `RaumVertretungsTag`
    * Subklasse von `VertretungsTag`
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
* `Klausur`
    * Ein primitives Datenmodell, ähnlich zu `Aufsicht`, das Informationen über eine Klausur enthält
    * Wird von `Klasse.klausuren` erzeugt

### 🔧 Änderungen

* `Vertretungsplan` und `.fetch()` wurden angepasst, um die neuen Vertretungsplanarten verarbeiten zu können
* `Vertretungsplan.bulkfetch()` wurde entfernt
* `InvalidCredentialsError` wurde in `Unauthorized` umbenannt
* `VertretungsTag.freieTage` gibt statt `None` nun `[]` zurück
* `VertretungsTag.datum` parst jetzt nicht mehr den Dateinamen sondern den XML-Tag `DatumPlan`
* `VertretungsTag.klassen`, `.lehrer` und `.räume` geben nun ein Dictionary zurück. Die Schlüssel sind die jeweiligen Kürzel, die Werte sind die jeweiligen Klasseninstanzen
* `VertretungsTag.klasse()`, `.get_lehrer()` und `.raum()` wurden entfernt
* `Klasse.stundenHeute` wurde in `.stunden` und `.stundenHeuteInPeriode` in `.stundenInPeriode` umbenannt
* `Klasse.stundenInPeriode()` gibt nun `[]` statt `None` zurück
* `Klasse.kurse` gibt nun ein Dictionary zurück. Die Schlüssel sind die jeweiligen Kürzel, die Werte sind die jeweiligen Kursinstanzen
* `Stunde.raum` wurde durch `Stunde.räume` ersetzt, das nun eine Liste von Strings zurückgibt. Statt `None` wird `[]` zurückgegeben
* `Stunde.lehrer` gibt nun eine Liste von Strings zurück. Statt `None` wird `[]` zurückgegeben
* `Stunde.ausfall` ist nun auch `True`, wenn die Stundeninfo `"selbst"` enthält und Lehrer und Räume nicht vorhanden sind
* `Kurs.gruppe` wurde in `.kürzel` umbenannt. Es gibt jetzt als Fallback `.fach` zurück
* Alle Properties, die Klassen, Lehrer oder Räume zurückgeben, verwenden nun das Trennzeichen, das in `config.SEPARATOR` festgelegt werden kann, um Mehrfachnennungen zu trennen
* Alle Properties wurden `None`-sicher gemacht, sodass sie nun keine Fehler mehr werfen können, sollte ein Tag in der Quelldatei unerwarteter Weise nicht vorhanden sein
* Aufzählungen von Klassen können nun auch Bereiche (z.B. `"5a-7c"`) enthalten und werden aufgelöst. Das Format einer Klassenbezeichnung kann in `config` durch ein Pattern konfiguriert werden. Die Capturing Groups `stufe` und `suffix` müssen enthalten sein

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
