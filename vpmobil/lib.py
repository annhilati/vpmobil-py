import xml.etree.ElementTree as ET
import xml.dom.minidom as MD

def prettyxml(object: ET.Element | ET.ElementTree) -> str:
    if isinstance(object, ET.ElementTree):
        element = object.getroot()
    elif isinstance(object, ET.ElementTree):
        element = object
    else:
        element = object
    
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = MD.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")