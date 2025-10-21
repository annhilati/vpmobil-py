"""Erweiterung zum Umwandeln von Vertretungsplan-Datenmodellen

---

Mit den Funktionen dieses Submoduls können beispielsweise `VertretungsTag`-Objekte (mit geringfügigen Einbußen) in `VertretungsTagLehrer`-Objekte umgewandelt werden,
um so eine Auswertung aus Perspektive der Lehrer zu ermöglichen.
"""

from typing import Callable, Literal
from vpmobil.models import (
    VertretungsTag as VT, VertretungsTagLehrer as VTL, VertretungsTagRäume as VTR, MobdatenBase,
    Stunde,
    VertretungsTagType, KlasseLikeType
)
from vpmobil import config
import xml.etree.ElementTree as XML

def _converter(
    planart:     Literal["K", "L", "R"],
    get_Le:      Callable[[Stunde], list[str]],
    get_LeAe:    Callable[[Stunde], bool],
    get_Ra:      Callable[[Stunde], list[str]],
    get_RaAe:    Callable[[Stunde], bool],
    get_Kl:      Callable[[VertretungsTagType], list[KlasseLikeType]],
    get_will_Kl: Callable[[Stunde], list[str]],
):
    def _subElement(parent: XML.Element, tag: str, text: str = None, attrib: dict = {}) -> XML.Element:
        element = XML.SubElement(parent, tag, attrib)
        if text: element.text = text
        return element

    def converter(tag: VT | VTL | VTR):
        """Aus welchem Attribut bekomme ich xyz für den neuen Plan?"""
        root = XML.Element("VpMobil")

        Kopf = _subElement(root, "Kopf")
        _subElement(Kopf, "planart", planart)
        _subElement(Kopf, "zeitstempel", tag.zeitstempel.strftime("%d.%m.%Y, %H:%M"))
        _subElement(Kopf, "DatumPlan", tag.datum.strftime("%A, %d. %B %Y"))

        FreieTage = _subElement(root, "FreieTage")
        for datum in tag.freieTage:
            _subElement(FreieTage, "ft", datum.strftime("%y%m%d"))

        Klassen = _subElement(root, "Klassen")
        target_map = {}
        seen: set[tuple] = set()

        for klasseLike in get_Kl(tag):
            for periode, stunden in klasseLike.stunden.items():
                for stunde in stunden:
                    for target in get_will_Kl(stunde):
                        key = (
                            target,
                            stunde.periode,
                            stunde.fach or "",
                            tuple(sorted(get_Le(stunde))),
                            tuple(sorted(get_Ra(stunde))),
                        )
                        if key in seen:
                            continue
                            # Um zu vermeiden, dass im resultierenden Plan mehrmals die selbe Stunde steht, nur weil sie aus dem Quellplan bei verschiedenen Klassenartigen vorkam
                        seen.add(key)

                        if target not in target_map:
                            Kl = _subElement(Klassen, "Kl")
                            _subElement(Kl, "Kurz", target)
                            Pl = _subElement(Kl, "Pl")
                            target_map[target] = Pl
                        else:
                            Pl = target_map[target]

                        Std = _subElement(Pl, "Std")
                        _subElement(Std, "St", str(stunde.periode))
                        _subElement(Std, "Beginn", stunde.beginn.strftime("%H:%M"))
                        _subElement(Std, "Ende", stunde.ende.strftime("%H:%M"))

                        fa_text = "" if stunde.fach is None and not stunde.ausfall else stunde.fach if not stunde.ausfall else "---"
                        Fa = _subElement(Std, "Fa", fa_text)
                        if stunde.fachgeändert:
                            Fa.set("FaAe", "FaGeaendert")

                        Le = _subElement(Std, "Le", config.SEPARATOR.join(get_Le(stunde)))
                        if get_LeAe(stunde):
                            Le.set("LeAe", "LeGeaendert")

                        Ra = _subElement(Std, "Ra", config.SEPARATOR.join(get_Ra(stunde)))
                        if get_RaAe(stunde):
                            Ra.set("RaAe", "RaGeaendert")

                        if getattr(stunde, "kursnummer", None):
                            _subElement(Std, "Nr", str(stunde.kursnummer))
                        if getattr(stunde, "info", None):
                            _subElement(Std, "If", stunde.info)

        return MobdatenBase(XML.ElementTree(root))

    return converter


def VertretungsTag(tag: VTL | VTR) -> VT:
    if type(tag) == VTL:
        return _converter(
            planart=     "K",
            get_Le=      lambda s: s.klassen,
            get_LeAe=    lambda s: s.klassegeändert,
            get_Ra=      lambda s: s.räume,
            get_RaAe=    lambda s: s.raumgeändert,
            get_Kl=      lambda d: d.lehrer,
            get_will_Kl= lambda s: s.klassen
        )(tag)
    elif type(tag) == VTR:
        return _converter(
            planart=     "K",
            get_Le=      lambda s: s.lehrer,
            get_LeAe=    lambda s: s.lehrergeändert,
            get_Ra=      lambda s: s.räume,
            get_RaAe=    lambda s: s.raumgeändert,
            get_Kl=      lambda d: d.räume,
            get_will_Kl= lambda s: s.klassen
        )(tag)
    else:
        raise ValueError(f"Unzulässiger Plantyp: {type(tag)}")
    
def VertretungsTagLehrer(tag: VT | VTR) -> VTL:
    if type(tag) == VT:
        return _converter(
            planart=     "L",
            get_Le=      lambda s: s.lehrer,
            get_LeAe=    lambda s: s.lehrergeändert,
            get_Ra=      lambda s: s.räume,
            get_RaAe=    lambda s: s.raumgeändert,
            get_Kl=      lambda d: d.klassen,
            get_will_Kl= lambda s: s.lehrer
        )(tag)
    elif type(tag) == VTR:
        return _converter(
            planart=     "L",
            get_Le=      lambda s: s.lehrer,
            get_LeAe=    lambda s: s.lehrergeändert,
            get_Ra=      lambda s: s.räume,
            get_RaAe=    lambda s: s.raumgeändert,
            get_Kl=      lambda d: d.räume,
            get_will_Kl= lambda s: s.lehrer
        )(tag)
    else:
        raise ValueError(f"Unzulässiger Plantyp: {type(tag)}")
    
def VertretungsTagRäume(tag: VT | VTL) -> VTR:
    if type(tag) == VT:
        return _converter(
            planart=     "R",
            get_Le=      lambda s: s.lehrer,
            get_LeAe=    lambda s: s.lehrergeändert,
            get_Ra=      lambda s: s.räume,
            get_RaAe=    lambda s: s.raumgeändert,
            get_Kl=      lambda d: d.klassen,
            get_will_Kl= lambda s: s.räume
        )(tag)
    elif type(tag) == VTL:
        return _converter(
            planart=     "R",
            get_Le=      lambda s: s.klassen,
            get_LeAe=    lambda s: s.klassegeändert,
            get_Ra=      lambda s: s.räume,
            get_RaAe=    lambda s: s.raumgeändert,
            get_Kl=      lambda d: d.lehrer,
            get_will_Kl= lambda s: s.räume
        )(tag)
    else:
        raise ValueError(f"Unzulässiger Plantyp: {type(tag)}")