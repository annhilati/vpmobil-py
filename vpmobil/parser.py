from dataclasses import dataclass, fields
from string import ascii_lowercase
import re, copy

@dataclass
class Parser:
    """Die `Parser`-Klasse beinhält Parameter für die Auswertung von Zeichenketten,
    die durch Konvention oder Eigenheiten des Vertretungsplaners unterschiedlich
    sein können.
    
    Parameters:
        AUFZÄHLUNGS_TRENNZEICHEN (str): Zeichen das verwendet wird, um etwaige
            Mehrfachnennungen von Lehrern, Räumen oder Klassen aufzutrennen

            Wenn der Vertretungsplaner Klassen wie
            - `"10a, 10b"` einträgt, sollte der Separator `", "` und bei
            - `"10a 10b"` beispielsweise `" "` sein.

            Wenn der Planer inkonsistent in seiner Syntax ist, sollte Auswertung nur
            für alle angegebenen Klassen gemeinsam gemacht werden.
        BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN (bool):
            Ob `-` in Klassenangaben als Bereich interpretiert werden sollen

            Falls ja würde
            - `"10a-10c"` als `"10a", "10b", "10c"` und
            - `"8a-10a"` als `"8a", "9a", "10a"` interpretiert.
        KLASSENBEZEICHNER_PATTERN (str): Capture-Pattern für Stufe und Suffix einer
            Klasse. Die Capture-Groups `stufe` und `suffix` müssen enthalten sein.
        STUNDE_HERVERLEGT_PATTERN (str):
            Capture-Pattern, dass die Periode, von der eine Stunde verleg wurde,
            extrahiert. Muss die Capture-Group `periode` enthalten
    """
    
    AUFZÄHLUNGS_TRENNZEICHEN: str = " "
    BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN: bool = True
    KLASSENBEZEICHNER_PATTERN: str = r"(?P<stufe>[1-9][0-9]?)(?P<suffix>[a-z])"
    STUNDE_HERVERLEGT_PATTERN: str = r"verlegt von St\.(?P<periode>\d+);"
    
    def clone(self, **overrides) -> "Parser":
        """Erzeugt eine Kopie des Parser-Objekts und überschreibt besimmt Felder.

        Ungültige Feldnamen erzeugen einen Fehler.
        """
        feldnamen = {field.name for field in fields(Parser)}

        ungueltig = set(overrides) - feldnamen
        if ungueltig:
            raise TypeError(
                f"Unbekannte Parser-Parameter: {', '.join(sorted(ungueltig))}"
            )

        instance = copy.deepcopy(self)

        for key, value in overrides.items():
            setattr(instance, key, copy.deepcopy(value))

        return instance
    
    def slice_aufzählung(self, string: str) -> list[str]:
        """Wandelt Aufzählungen in Strings in eine Liste von Strings um.
        
        Unterstützt auch Bereiche von Klassen, je nach `parser`.
        """

        if not string:
            return []

        parts = [p.strip() for p in string.split(self.AUFZÄHLUNGS_TRENNZEICHEN) if p.strip()]

        if not self.BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN:
            return parts

        result: list[str] = []

        for part in parts:
            if "-" not in part:
                result.append(part)
                continue

            start_raw, end_raw = part.split("-", 1)
            start_match = re.fullmatch(self.KLASSENBEZEICHNER_PATTERN, start_raw.strip())
            end_match = re.fullmatch(self.KLASSENBEZEICHNER_PATTERN, end_raw.strip())

            if not (start_match and end_match):
                # Fallback: unverständlicher Bereich, unverändert übernehmen
                result.append(part)
                continue

            s_stufe, s_suffix = start_match["stufe"], start_match["suffix"]
            e_stufe, e_suffix = end_match["stufe"], end_match["suffix"]

            # Unterscheide Zahlensuffix (z. B. 5/1–5/3) vs. Buchstabensuffix (z. B. 5a–5c)
            if s_suffix.isdigit() and e_suffix.isdigit():
                if s_stufe == e_stufe:
                    for i in range(int(s_suffix), int(e_suffix) + 1):
                        result.append(f"{s_stufe}/{i}")
                else:
                    for n in range(int(s_stufe), int(e_stufe) + 1):
                        result.append(f"{n}/{s_suffix}")  # fallback bei ungleicher stufe
                continue

            if s_suffix.isalpha() and e_suffix.isalpha():
                letters = list(ascii_lowercase)
                start_i = letters.index(s_suffix)
                end_i = letters.index(e_suffix)
                if s_stufe == e_stufe:
                    for c in letters[start_i:end_i + 1]:
                        result.append(f"{s_stufe}{c}")
                else:
                    for n in range(int(s_stufe), int(e_stufe) + 1):
                        for c in letters[start_i:end_i + 1]:
                            result.append(f"{n}{c}")
                continue

            result.append(part)

        return result