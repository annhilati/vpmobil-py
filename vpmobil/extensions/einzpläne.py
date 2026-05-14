"""Erweiterung für die Asuwertung von EinzPläne-PDF-Dateien

---

EinzPläne-PDF-Dateien sind PDFs, die von der Indiware-Planungssoftware bereitgestellt werden und die Wochenpläne von Schüler einzeln untereinander als Tabelle enthalten.
"""

from pathlib import Path
import re

def check_dependency():
    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError(
            "Für PDF-Funktionen muss 'reportlab' installiert sein:\n"
            "pip install meinpaket[pdf]"
        ) from e

_NAME_RE = re.compile(
    r"^Plan für .*?:\s*(.*?)\s+Tutor(?:in)?\s*:",
    re.IGNORECASE
)

_PLAN_RE = re.compile(
    r"^Plan für .*?:\s*(.*?)\s+Tutor(?:in)?\s*:\s*(.*?)\s*$",
    re.IGNORECASE,
)

def _student_from_line(line: str) -> tuple[str, str]:
    """
    Erwartet z. B.:
    'Plan für Schülerin: Vulliet, Élise Tutor: Ah'
    """
    m = _NAME_RE.search(line.strip())
    if not m:
        raise ValueError(
            "Konnte den Schülernamen aus der Plan-Zeile nicht lesen. "
            "Das PDF scheint anders formatiert zu sein."
        )

    name = m.group(1).strip()

    if ", " not in name:
        raise ValueError(
            f"Unerwartetes Namensformat: {name!r}. Erwartet wird 'Nachname, Vorname'."
        )

    nachname, vorname = name.split(", ", 1)
    return vorname, nachname


def kurse(pfad: Path | str) -> dict[str, set[tuple[str, str]]]:
    """
    Extrahiert aus einem EinzPläne-PDF die Kurskürzel und die Namen zugehöriger Schüler.
    Die Namen werden als Tupel (Vorname, Nachname) gespeichert.
    """

    check_dependency()
    import pdfplumber

    pfad = Path(pfad)
    ergebnis: dict[str, set[tuple[str, str]]] = {}

    with pdfplumber.open(pfad) as pdf:
        if not pdf.pages:
            return ergebnis

        first_text = pdf.pages[0].extract_text() or ""
        if not first_text.startswith("Schulname"):
            raise ValueError(
                "Das PDF ist auf unbekannte Weise formatiert. Wenn du denkst, dass dies funktionieren sollte, "
                "melde diesen Fehler bitte im Issue-Tracker von vpmobil-py auf GitHub."
            )

        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [line.strip() for line in text.splitlines() if line.strip()]

            # Alle Schülernamen auf der Seite in der Reihenfolge der Tabellen sammeln
            schueler_namen: list[tuple[str, str]] = []
            for line in lines:
                if line.startswith("Plan für "):
                    schueler_namen.append(_student_from_line(line))

            if not schueler_namen:
                continue

            # Tabellen auslesen; bei diesem PDF funktionieren Linien am besten
            tables = page.extract_tables(
                table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "snap_tolerance": 3,
                    "join_tolerance": 3,
                    "intersection_tolerance": 3,
                    "edge_min_length": 3,
                    "min_words_vertical": 1,
                    "min_words_horizontal": 1,
                    "text_tolerance": 2,
                }
            )

            # Fallback, falls die Linienstrategie auf einer Seite mal schlechter greift
            if len(tables) != len(schueler_namen):
                alt_tables = page.extract_tables()
                if len(alt_tables) == len(schueler_namen):
                    tables = alt_tables

            if len(tables) != len(schueler_namen):
                raise ValueError(
                    f"Auf einer Seite wurden {len(schueler_namen)} Schülerblöcke, aber {len(tables)} Tabellen erkannt. "
                    "Die Zuordnung ist damit nicht eindeutig."
                )

            # Jede Tabelle gehört zum davor gefundenen Schüler
            for schueler, table in zip(schueler_namen, tables):
                if not table or len(table) < 2:
                    continue

                # erste Zeile ist die Wochentags-Überschrift
                for row in table[1:]:
                    # Spalte 0 ist die Stunden-Nummer, ab Spalte 1 stehen die Tage
                    for cell in row[1:]:
                        if not cell:
                            continue

                        cell = cell.strip()
                        if not cell:
                            continue

                        kurs = cell.split(None, 1)[0]
                        ergebnis.setdefault(kurs, set()).add(schueler)

    return dict(sorted(ergebnis.items()))

def _parse_plan_line(line: str) -> tuple[tuple[str, str], str]:
    """
    Gibt ((Vorname, Nachname), Tutor) zurück.
    """
    line = line.strip()
    m = _PLAN_RE.match(line)
    if not m:
        raise ValueError(f"Konnte die Plan-Zeile nicht lesen: {line!r}")

    name = m.group(1).strip()
    tutor = m.group(2).strip()

    if ", " not in name:
        raise ValueError(f"Unerwartetes Namensformat: {name!r}")

    nachname, vorname = name.split(", ", 1)
    return (vorname, nachname), tutor


def tutoren(pfad: Path | str) -> dict[str, list[tuple[str, str]]]:
    """Extrahiert aus einem EinzPläne-PDF die Tutoren und die Namen zugehöriger Schüler.

    Die Namen werden als 2-Tupel aus Vorname (und Mittelnamen) und Nachname übergeben.

    Parameters:
        pfad (Path | str): Pfad zu einer "EinzPläne"-PDF-Datei von Indiware

    Raises:
        ValueError: Wenn das PDF auf unbekannte Weise formatiert ist
    """

    check_dependency()
    import pdfplumber

    pfad = Path(pfad)
    ergebnis: dict[str, set[tuple[str, str]]] = {}

    with pdfplumber.open(pfad) as pdf:
        if not pdf.pages:
            return {}

        first_text = pdf.pages[0].extract_text() or ""
        if not first_text.startswith("Schulname"):
            raise ValueError(
                "Das PDF ist auf unbekannte Weise formatiert. Wenn du denkst, dass dies funktionieren sollte, "
                "melde diesen Fehler bitte im Issue-Tracker von vpmobil-py auf GitHub."
            )

        for page in pdf.pages:
            text = page.extract_text() or ""

            for line in text.splitlines():
                line = line.strip()
                if not line.startswith("Plan für "):
                    continue

                schüler, tutor = _parse_plan_line(line)
                ergebnis.setdefault(tutor, set()).add(schüler)

    return {
        tutor: sorted(schüler, key=lambda t: t[0])
        for tutor, schüler in sorted(ergebnis.items())
    }