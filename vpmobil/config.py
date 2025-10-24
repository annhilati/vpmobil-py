"""
Globale (Parsing-) Parameter für vpmobil-py

Parameter
---------
Parameter sind als Attribute von `config` ausles- und setzbar.

SEPARATOR : str = `" "`
    Zeichen das verwendet wird, um Mehrfachnennungen von Lehrern, Räumen oder Klassen aufzutrennen
INTERPRET_HYPHEN_AS_RANGE : bool = `True`
    Ob `-` in Klassenangaben als Bereich interpretiert werden sollen
"""

SEPARATOR = " "
"""Zeichen das verwendet wird, um etwaige Mehrfachnennungen von Lehrern, Räumen oder Klassen aufzutrennen

Wenn der Vertretungsplaner Klassen wie
- `"10a, 10b"` einträgt, sollte der Separator `", "` und bei
- `"10a 10b"` beispielsweise `" "` sein.

Wenn der Planer inkonsistent in seiner Syntax ist, sollte Auswertung nur für alle angegebenen Klassen gemeinsam gemacht werden.
"""

INTERPRET_HYPHEN_AS_RANGE = True
"""Ob `-` in Klassenangaben als Bereich interpretiert werden sollen

Falls ja würde
- `"10a-10c"` als `"10a", "10b", "10c"` und
- `"8a-10a"` als `"8a", "9a", "10a"` interpretiert.
"""

class ERRORS:
    KEY_VALUE_ASSERTION = "Die Konvertierung des Datenmodells ist fehlgeschlagen. Melde diesen Fall unbedingt im Bugtracker von vpmobil-py auf GitHub."
    UNKNOWN_XML = "XML-Quelldaten sind unbekannt formatiert"