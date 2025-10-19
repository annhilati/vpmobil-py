import xml.etree.ElementTree as XML
from vpmobil import VertretungsTag, VertretungsTagLehrer, Vertretungsplan, Stundenplan24Pfade
from vpmobil import config

def _subElement(parent: XML.Element, tag: str, text: str = None, attrib: dict = {}) -> XML.Element:
    element = XML.SubElement(parent, tag, attrib)
    if text: element.text = text
    return element

def lehrer_from_klassen(tag: VertretungsTag) -> VertretungsTagLehrer:

    root = XML.Element("VpMobil")

    Kopf            = _subElement(root, "Kopf")
    _subElement(Kopf, "planart", "L")
    _subElement(Kopf, "zeitstempel", tag.zeitstempel.strftime("%d.%m.%Y, %H:%M"))
    _subElement(Kopf, "DatumPlan", tag.datum.strftime("%A, %d. %B %Y"))

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
                        Kl = _subElement(Klassen, "Kl")
                        _subElement(Kl, "Kurz", lehrer)
                        Pl = _subElement(Kl, "Pl")
                        Pl_map[lehrer] = Pl
                    else:
                        Pl = Pl_map[lehrer]

                    Std = _subElement(Pl, "Std")
                    _subElement(Std, "St", str(stunde.periode))
                    _subElement(Std, "Beginn", stunde.beginn.strftime("%H:%M"))
                    _subElement(Std, "Ende", stunde.ende.strftime("%H:%M"))
                    if stunde.fach:             Fa = _subElement(Std, "Fa", stunde.fach)
                    elif stunde.ausfall:        Fa = _subElement(Std, "Fa", "---")
                    if stunde.fachgeändert:     Fa.set("FaAe", "FaGeaendert")

                    Le = _subElement(Std, "Le", config.SEPARATOR.join(stunde.klassen)) # wird bei leerer Liste ""
                    if stunde.klassegeändert: 
                        Le.set("LeAe", "LeGeaendert")

                    Ra = _subElement(Std, "Ra", config.SEPARATOR.join(stunde.räume)) # wird bei leerer Liste ""
                    if stunde.raumgeändert:
                        Ra.set("RaAe", "RaGeaendert")
                    if stunde.kursnummer:       _subElement(Std, "Nr", str(stunde.kursnummer))
                    if stunde.info:             _subElement(Std, "If", stunde.info)

    return VertretungsTagLehrer(XML.ElementTree(root))