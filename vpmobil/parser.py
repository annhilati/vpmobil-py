from dataclasses import dataclass

@dataclass
class Parser:
    
    AUFZÄHLUNGS_TRENNZEICHEN: str = " "
    """Zeichen das verwendet wird, um etwaige Mehrfachnennungen von Lehrern,
    Räumen oder Klassen aufzutrennen

    Wenn der Vertretungsplaner Klassen wie
    - `"10a, 10b"` einträgt, sollte der Separator `", "` und bei
    - `"10a 10b"` beispielsweise `" "` sein.

    Wenn der Planer inkonsistent in seiner Syntax ist, sollte Auswertung nur
    für alle angegebenen Klassen gemeinsam gemacht werden.
    """

    BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN: bool = True
    """Ob `-` in Klassenangaben als Bereich interpretiert werden sollen

    Falls ja würde
    - `"10a-10c"` als `"10a", "10b", "10c"` und
    - `"8a-10a"` als `"8a", "9a", "10a"` interpretiert.
    """

    KLASSENBEZEICHNER_PATTERN: str = r"(?P<stufe>[1-9][0-9]?)(?P<suffix>[a-z])"
    """Capture-Pattern für Stufe und Suffix einer Klasse. Die Capture-Groups
    `stufe` und `suffix` müssen enthalten sein.
    """

    STUNDE_HERVERLEGT_PATTERN: str = r"verlegt von St\.(?P<periode>\d+);"
    """Capture-Pattern, dass die Periode, von der eine Stunde verleg wurde, extrahiert.  
    Muss die Capture-Group `periode` enthalten"""