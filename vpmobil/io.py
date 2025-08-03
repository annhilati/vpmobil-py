import xml.etree.ElementTree as XML

from pathlib import Path

from .models import VpDay

def parsefromfile(pfad: Path) -> VpDay:
    """
    Erstellt ein VpDay-Objekt aus den XML-Daten einer Datei

    #### Argumente:
        pfad: Dateipfad der XML-Datei

    #### Returns:
        VpDay: Das VpDay-Objekt mit den entsprechenden Daten

    #### Raises:
        FileNotFoundError: Wenn die Datei nicht existiert
        Exception: Wenn die DAtei nicht gelesen werden oder in ein XML-Element umgewandelt werden konnte
    """
    with open(pfad) as f:
        vpday = VpDay(_data=XML.parse(f))
    return vpday