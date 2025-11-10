"""
Globale (Parsing-) Parameter für vpmobil-py

Parameter
---------
Parameter sind als Attribute von `config` ausles- und setzbar.

AUFZÄHLUNGS_SEPARATOR : str = `" "`
    Zeichen das verwendet wird, um Mehrfachnennungen von Lehrern, Räumen oder Klassen aufzutrennen
BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN : bool = `True`
    Ob `-` in Klassenangaben als Bereich interpretiert werden sollen
KLASSENBEZEICHNER_PATTERN : str
    Capture-Pattern zum parsen von Klassenbezeichnungen
"""

def set_config(overrides: dict[str], /) -> None:
    "Setzt Parameter anhand von Keys"
    import sys
    config = sys.modules[__name__]

    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Ungültiger Parameter: {key}")

AUFZÄHLUNGS_SEPARATOR = " "
"""Zeichen das verwendet wird, um etwaige Mehrfachnennungen von Lehrern, Räumen oder Klassen aufzutrennen

Wenn der Vertretungsplaner Klassen wie
- `"10a, 10b"` einträgt, sollte der Separator `", "` und bei
- `"10a 10b"` beispielsweise `" "` sein.

Wenn der Planer inkonsistent in seiner Syntax ist, sollte Auswertung nur für alle angegebenen Klassen gemeinsam gemacht werden.
"""

BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN = True
"""Ob `-` in Klassenangaben als Bereich interpretiert werden sollen

Falls ja würde
- `"10a-10c"` als `"10a", "10b", "10c"` und
- `"8a-10a"` als `"8a", "9a", "10a"` interpretiert.
"""

KLASSENBEZEICHNER_PATTERN = r"(?P<stufe>[1-9][0-9]?)(?P<suffix>[a-z])"
"""Capture Pattern für Stufe und Suffix einer Klasse<br>
Muss die Capture-Groups `stufe` und `suffix` enthalten
"""

# STUNDENVERSCHIEBUNG_PATTERN = re.compile(
#     r"statt\s+"
#     r"(?P<wochentag1>[A-ZÄÖÜa-zäöü]{2})\s*\((?P<datum1>\d{1,2}\.\d{1,2}\.)\)\s*"
#     r"St\.?\s*(?P<stunde1>\d+);\s*"
#     r"(?P<fach>[A-ZÄÖÜa-zäöü]+)\s+"
#     r"(?P<titel>Herr|Frau)\s+"
#     r"(?P<name>[A-ZÄÖÜa-zäöü]+)\s+"
#     r"gehalten\s+am\s+"
#     r"(?P<wochentag2>[A-ZÄÖÜa-zäöü]{2})\s*\((?P<datum2>\d{1,2}\.\d{1,2}\.)\)\s*"
#     r"St\.?\s*(?P<stunde2>\d+)"
# )
"""
Das Format, in dem in den Informationen zu einer Stunde eine Verschiebung vermerkt wird.

Standard: `statt Mo (27.10.) St.6; ETH Herr Reinhold gehalten am Di (28.10.) St.4`
"""

class ERRORS:
    KEY_VALUE_ASSERTION = "Die Konvertierung des Datenmodells ist fehlgeschlagen. Melde diesen Fall unbedingt im Bugtracker von vpmobil-py auf GitHub."
    UNKNOWN_XML = "XML-Quelldaten sind unbekannt formatiert"