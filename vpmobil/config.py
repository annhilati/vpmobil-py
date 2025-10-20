"""
Globale (Parsing-) Parameter für vpmobil-py

Parameter
---------
SEPARATOR : str
    Zeichen das verwendet wird, um Mehrfachnennungen von Lehrern, Räumen oder Klassen aufzutrennen
"""

SEPARATOR = " "
"""Zeichen das verwendet wird, um etwaige Mehrfachnennungen von Lehrern, Räumen oder Klassen aufzutrennen

- `"10a, 10b"` -> `SEPARATOR = ", "`
- `"10a 10b"` -> `SEPARATOR = " "`
- etc.
"""

INTERPRET_HYPHEN_AS_RANGE = True
"""Ob `-` in Klassenangaben als Bereich interpretiert werden sollen

Falls ja würde
- `"10a-10c"` als `"10a", "10b", "10c"` und
- `"8a-10a"` als `"8a", "9a", "10a"` interpretiert.
"""