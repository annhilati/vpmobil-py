import xml.etree.ElementTree as ET
import xml.dom.minidom as MD

def prettyxml(object: ET.Element | ET.ElementTree) -> str:
    if isinstance(object, ET.ElementTree):
        element = object.getroot()
    elif isinstance(object, ET.ElementTree):
        element = object
    else:
        element = object
    
    string = ET.tostring(element, 'utf-8')
    reparsed = MD.parseString(string)
    return reparsed.toprettyxml(indent="\t")