import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
from enum import StrEnum

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

class StandardPfade(StrEnum):
    PlanKl = "/mobil/mobdaten/PlanKl{yyyymmdd}.xml"
    PlanLe = "/moble/mobdaten/PlanLa{yyyymmdd}.xml"
    PlanRa = "/mobra/mobdaten/PlanRa{yyyymmdd}.xml"