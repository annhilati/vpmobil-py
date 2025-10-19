import xml.etree.ElementTree as XML
from vpmobil import VertretungsTag, VertretungsTagLehrer, Vertretungsplan, Stundenplan24Pfade
from vpmobil import config

def subElement(parent: XML.Element, tag: str, text: str = None, attrib: dict = {}) -> XML.Element:
    element = XML.SubElement(parent, tag, attrib)
    if text: element.text = text
    return element

def lehrer_from_klassen(tag: VertretungsTag) -> VertretungsTagLehrer:

    root = XML.Element("VpMobil")

    Kopf            = subElement(root, "Kopf")
    subElement(Kopf, "planart", "L")
    subElement(Kopf, "zeitstempel", tag.zeitstempel.strftime("%d.%m.%Y, %H:%M"))
    subElement(Kopf, "DatumPlan", tag.datum.strftime("%A, %d. %B %Y"))

    FreieTage       = XML.SubElement(root, "FreieTage")
    for datum in tag.freieTage:
        ft = XML.SubElement(FreieTage, "ft")
        ft.text = datum.strftime("%y%m%d")

    Klassen         = XML.SubElement(root, "Klassen")

    Pl_map = {}

    for klasse in tag.klassen:
        for periode, stunden in klasse.stunden.items():
            for stunde in stunden:
                for lehrer in stunde.lehrer:

                    if lehrer not in Pl_map:
                        Kl = subElement(Klassen, "Kl")
                        subElement(Kl, "Kurz", lehrer)
                        Pl = subElement(Kl, "Pl")
                        Pl_map[lehrer] = Pl
                    else:
                        Pl = Pl_map[lehrer]

                    Std = subElement(Pl, "Std")
                    subElement(Std, "St", str(stunde.periode))
                    subElement(Std, "Beginn", stunde.beginn.strftime("%H:%M"))
                    subElement(Std, "Ende", stunde.ende.strftime("%H:%M"))
                    if stunde.fach:
                        subElement(Std, "Fa", stunde.fach)
                    if stunde.klassen:
                        subElement(Std, "Le", config.SEPARATOR.join(stunde.klassen))
                    if stunde.räume:
                        subElement(Std, "Ra", config.SEPARATOR.join(stunde.räume))
                    if stunde.kursnummer:
                        subElement(Std, "Nr", str(stunde.kursnummer))
                    if stunde.info:
                        subElement(Std, "If", stunde.info)

    return VertretungsTagLehrer(XML.ElementTree(root))