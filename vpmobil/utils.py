from typing import Any, overload, Literal
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD

def prettyxml(object: ET.Element | ET.ElementTree) -> str:
    if isinstance(object, ET.ElementTree):
        element = object.getroot()
    elif isinstance(object, ET.Element):
        element = object
    else:
        raise TypeError
    
    string = ET.tostring(element, 'utf-8')
    reparsed = MD.parseString(string)
    return reparsed.toprettyxml(indent="\t")


@overload
def find(element: ET.Element, path: str, mode: Literal["text"]) -> str | Literal[""]: ...
@overload
def find(element: ET.Element, path: str, mode: Literal["attrib"]) -> dict: ...
def find(element: ET.Element, path: str, mode: Literal["text", "attrib"]):
    target = element.find(path)
    if target is None:
        target = ET.Element(path.split('/')[-1])
    match mode:
        case "text":    return getattr(target, "text", "")
        case "attrib":  return getattr(target, "attrib", {})
        case _:         raise ValueError


# def SubElement(parent: ET.Element, tag: str, text: str | Any = None, attrib: dict = {}) -> ET.Element:
#         element = ET.SubElement(parent, tag, attrib)
#         if text:
#             element.text = str(text)
#         return element
    
def ElementBuilder(tag: str, text: str | Any | None = None, attrib: dict[str] = {}, *, children: list[ET.Element | None] = []) -> ET.Element:
    "Jedes None in `children` wird ignoriert und nicht angehangen"
    element = ET.Element(tag, attrib)
    if text:
        element.text = str(text)
    element.extend([c for c in children if c is not None])
    return element