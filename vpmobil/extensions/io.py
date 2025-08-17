import xml.etree.ElementTree as XML

from pathlib import Path

from vpmobil.models import VertretungsTag

def parsefromfile(pfad: Path) -> VertretungsTag:
    """
    Erstellt ein VpDay-Objekt aus einer XML-Vertretungsplandatei vom Typ K

    Parameter
    ----------
    pfad: Path
        Dateipfad einer XML-Datei vom Typ K

    Raises
    ----------
    FileNotFoundError : Wenn die Datei nicht existiert
    ValueError : Wenn die Datei nicht gelesen werden kann
    """
    with open(pfad) as f:
        vpday = VertretungsTag(_data=XML.parse(f))
    return vpday