from .parser import VpDay, Klasse, Stunde
import xml.etree.ElementTree as XML
from acemeta import fileToStr

def getxml(object: VpDay | Klasse | Stunde) -> XML.ElementTree | XML.Element:
    """
    Gibt die XML Daten eines Objekts als Klasse des xml-Moduls zurück

    #### Argumente
        object (VpDay | Klasse | Stunde): Vertretungsplan-Objekt, aus dem die XML-Daten isoliert werden sollen

    #### Returns
        ElementTree: Wenn object einen VpDay-Objekt ist
        Element: Wenn object einen Klassen-Objekt ist
        Element: Wenn object einen Stunden-Objekt ist
    """

    if isinstance(object, VpDay): return object._mobdaten
    elif isinstance(object, Klasse): return object._data
    elif isinstance(object, Stunde): return object._data
    else: raise TypeError("object muss einer der Typen VpDay, Klasse & Stunde sein") # Der Code ist ereichbar lol habs getestet

def parsefromfile(pfad: str):
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
    return VpDay(mobdaten=fileToStr(file=pfad))