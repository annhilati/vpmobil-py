import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
from enum import StrEnum
from datetime import date, timedelta

def prettyxml(object: ET.Element | ET.ElementTree) -> str:
    if isinstance(object, ET.ElementTree):
        element = object.getroot()
    elif isinstance(object, ET.Element):
        element = object
    else:
        element = object
    
    string = ET.tostring(element, 'utf-8')
    reparsed = MD.parseString(string)
    return reparsed.toprettyxml(indent="\t")

class Stundenplan24Pfade(StrEnum):
    """Enumerator mit den Pfaden für Vertretungsplanquelldateien, wie sie auf `stundenplan24.de` verwendet werden.<br>
    Enthalten den `{schulnummer}`- und `date`-Platzhalter"""
    Klassen = "{schulnummer}/mobil/mobdaten/Klassen.xml"
    PlanKl  = "{schulnummer}/mobil/mobdaten/PlanKl%Y%m%d.xml"
    Lehrer  = "{schulnummer}/moble/mobdaten/Lehrer.xml"
    PlanLe  = "{schulnummer}/moble/mobdaten/PlanLe%Y%m%d.xml"
    Raeume  = "{schulnummer}/mobra/mobdaten/Raeume.xml"
    PlanRa  = "{schulnummer}/mobra/mobdaten/PlanRa%Y%m%d.xml"

def date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)