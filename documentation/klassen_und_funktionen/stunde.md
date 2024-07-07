# Stunde()

Enthält Informationen über eine bestimmten Stunde.

## Klasse

```python
class Stunde(elem: XML.Element | bytes | str)
```
Nimmt ein `XML.Element`, welches ein `<Std>` - Element im XML Tree ist.

## Eigenschaften

* `.nr: int` - Nummer der Stunde
* `.beginn: str` - Beginn der Stunde als str()
* `.ende: str` - Ende der Stunde als str()
* `.anders: bool` - Gibt an, ob irgendeine Eigenschaft dieser Stunde geändert ist
* `.entfaellt: bool` - Gibt an, ob die Stunde entfällt. Wenn ja, werden 'lehrer', 'fach' und 'raum' leere Strings zurückgeben
* `.fach: str` - Gibt das Fach, welches in dieser Stunde stattfindet zurück. Gibt einen leeren String zurück, wenn die Stunde entfällt
* `.lehrer: str` - Gibt den Lehrer, welcher diese Stunde hält zurück .Gibt einen leeren String zurück, wenn die Stunde entfällt
* `.raum: str` - Gibt den Raum, in dem diese Stunde stattfindet zurück. Gibt einen leeren String zurück, wenn die Stunde entfällt
* `.kursnummer: str` - Gibt die Nummer des Kurses zurück. Nützlich für das Kurs() Objekt (kommt noch)
* `.info: str` - Gibt eine optionale vom Planer verfasste Information zu dieser Stunde. Ist nur in besonderen Situationen und bei entfallen der Stunde vorhanden

## Funktionen