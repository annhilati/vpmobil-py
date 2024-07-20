# Kurs()

Enthält Informationen über einen bestimmten Kurs.

## Klasse

```python
class Kurs(elem: XML.Element | bytes | str)
```
Nimmt ein `XML.Element`, welches ein `<Ue>` - Element im XML Tree ist.

## Eigenschaften

* `.fach: str` - Gibt das Fach, welches in diesem Kurs stattfindet zurück.
* `.zusatz: str` - Gibt ein Zusätzliches Fach (z.B. Fördern) zurück. Gibt einen leeren String zurück, wenn es kein Zusatzfach gibt.
* `.lehrer: str` - Gibt den Lehrer, welcher diesen Kurs hält.
* `.kursnummer: str` - Gibt die Nummer des Kurses zurück.
<br>**Wichtig:**<br>Das Kurs-Objekt hat den wichtigen Unterschied zu einem Stunden-Objekt, dass es **nur Lehrer, Fach, Zusatz und Kursnummer** hat.

## Funktionen