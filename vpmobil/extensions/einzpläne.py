from PyPDF2 import PdfReader
from pathlib import Path

def kurse(pfad: Path | str) -> dict[str, set[tuple[str, str]]]:
    """Extrahiert aus einem EinzPläne-PDF die Kurskürzel und die Namen zugehöriger Schüler

    Die Namen werden als 2-Tupeln aus Vorname (und Mittelnamen) und Nachname übergeben.

    Parameter
    ----------
    pfad : Path | str
        Pfad zu einer "EinzPläne"-PDF-Datei von Indiware

    Raises
    ----------
    ValueError : Wenn das PDF auf unbekannte Weise formatiert ist
    """
    
    reader = PdfReader(pfad)

    seiten = [seite.extract_text() for seite in reader.pages]

    kurse: dict[str, set[tuple]] = {}

    if not seiten[0].startswith("Schulname"):
        raise ValueError("Das PDF ist auf unbekannte Weise formatiert. Wenn du denkst, dass dies funktionieren sollte, melde diesen Fehler bite im Issue-Tracker von vpmobil-py auf GitHub.")

    for seite in seiten:
        for zeile in seite.splitlines():
            if "Montag" in zeile:
                name = zeile.split("Freitag")[1]
                schüler = (name.split(", ")[1], name.split(", ")[0])
            elif zeile[0].isnumeric():
                values = zeile[1:].split() # Erstes zeichen entfernen, weil es die Periode ist
                
                # Der extrahierte Text enthält pro Zeile immer konsektutiv 0-5 Kurse, dementsprechend viele Lehrer und so viele Räume. Allerdings is zwischen dem letzten Lehrer und dem ersten Raum manchmal kein Leerzeichen.
                if len(values) % 3 == 0:
                    magic = int(len(values) / 3)
                elif (len(values) + 1) % 3 == 0:
                    magic = int((len(values) + 1) / 3)
                else:
                    raise ValueError("Das PDF ist auf unbekannte Weise formatiert und kann nicht vollumfänglich ausgewertet werden. Bitte melde diesen Fehler unbedingt im Issue-Tracker von vpmobil-py auf GitHub.")

                for value in values[:magic]: 
                    if value not in kurse:
                        kurse[value] = {schüler}
                    else:
                        kurse[value].add(schüler)

    return {
        key: sorted(value, key=lambda t: t[0])
        for key, value in sorted(kurse.items())
    }

def tutoren(pfad: Path | str) -> dict[str: set[tuple[str, str]]]:
    """Extrahiert aus einem EinzPläne-PDF die Tutoren und die Namen zugehöriger Schüler

    Die Namen werden als 2-Tupeln aus Vorname (und Mittelnamen) und Nachname übergeben.

    Parameter
    ----------
    pfad : Path | str
        Pfad zu einer "EinzPläne"-PDF-Datei von Indiware

    Raises
    ----------
    ValueError : Wenn das PDF auf unbekannte Weise formatiert ist
    """

    reader = PdfReader(pfad)

    seiten = [seite.extract_text() for seite in reader.pages]

    tutoren: dict[str: set[tuple]] = {}

    if not seiten[0].startswith("Schulname"):
        raise ValueError("Das PDF ist auf unbekannte Weise formatiert. Wenn du denkst, dass dies funktionieren sollte, melde diesen Fehler bite im Issue-Tracker von vpmobil-py auf GitHub.")
    
    for seite in seiten:
        for zeile in seite.splitlines():
            if zeile.startswith("Plan für Schüler"):
                tutor = zeile.split(": ")[-1]
            elif zeile.startswith("Montag"):
                name = zeile.split("Freitag")[1]
                schüler = (name.split(", ")[1], name.split(", ")[0])
                if tutor not in tutoren:
                    tutoren[tutor] = {schüler}
                else:
                    tutoren[tutor].add(schüler)

    return {
        key: sorted(value, key=lambda t: t[0])
        for key, value in sorted(tutoren.items())
    }