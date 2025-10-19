from typing import Callable, Iterable
from vpmobil.models import (
    VertretungsTag, VertretungsTagLehrer, VertretungsTagRäume, MobdatenBase,
    Lehrer, Klasse, Raum
)
from vpmobil import config
import xml.etree.ElementTree as XML

def _subElement(parent: XML.Element, tag: str, text: str = None, attrib: dict = {}) -> XML.Element:
    element = XML.SubElement(parent, tag, attrib)
    if text: element.text = text
    return element

def _safe_getattr(obj, name, default=False):
    return getattr(obj, name, default)

def make_converter(
    planart_char: str,
    le_source: str,
    leAe_source: str,
    ra_source: str,
    raAe_source: str,
    kl_source: str,
    target_source: str
):
    def converter(tag: VertretungsTag | VertretungsTagLehrer | VertretungsTagRäume):
        root = XML.Element("VpMobil")

        Kopf = _subElement(root, "Kopf")
        _subElement(Kopf, "planart", planart_char)
        _subElement(Kopf, "zeitstempel", tag.zeitstempel.strftime("%d.%m.%Y, %H:%M"))
        _subElement(Kopf, "DatumPlan", tag.datum.strftime("%A, %d. %B %Y"))

        FreieTage = _subElement(root, "FreieTage")
        for datum in tag.freieTage:
            _subElement(FreieTage, "ft", datum.strftime("%y%m%d"))

        Klassen = _subElement(root, "Klassen")
        target_map = {}

        klasseLike: Klasse | Lehrer | Raum
        for klasseLike in _safe_getattr(tag, kl_source):
            for periode, stunden in klasseLike.stunden.items():
                for stunde in stunden:
                    target: str
                    for target in _safe_getattr(stunde, target_source):
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

                        # Fa immer anlegen (Platzhalter falls nötig)
                        fa_text = "" if stunde.fach is None and not stunde.ausfall else stunde.fach if not stunde.ausfall else "---"
                        Fa = _subElement(Std, "Fa", fa_text)
                        if stunde.fachgeändert:
                            Fa.set("FaAe", "FaGeaendert")

                        # Le (inhalt abhängig von caller)
                        Le = _subElement(Std, "Le", config.SEPARATOR.join(_safe_getattr(stunde, le_source)))
                        if _safe_getattr(stunde, leAe_source):
                            Le.set("LeAe", "LeGeaendert")

                        # Ra (inhalt abhängig von caller)
                        Ra = _subElement(Std, "Ra", config.SEPARATOR.join(_safe_getattr(stunde, ra_source)))
                        if _safe_getattr(stunde, raAe_source):
                            Ra.set("RaAe", "RaGeaendert")

                        if _safe_getattr(stunde, "kursnummer", None):
                            _subElement(Std, "Nr", str(stunde.kursnummer))
                        if _safe_getattr(stunde, "info", None):
                            _subElement(Std, "If", stunde.info)

        return MobdatenBase(XML.ElementTree(root))

    return converter

# Spezialisierungen für deine beiden Fälle:
lehrer_from_klassen = make_converter(
    planart_char="L",
    le_source="lehrer",
    leAe_source="lehrergeändert",
    ra_source="räume",
    raAe_source="raumgeändert",
    kl_source="klassen",
    target_source="lehrer"
)

klassen_from_räume = make_converter(
    planart_char="R",
    le_source="lehrer",
    leAe_source="lehrergeändert",
    ra_source="räume",
    raAe_source="raumgeändert",
    kl_source="klassen",
    target_source="räume"
)

klassen_from_räume = make_converter(
    planart_char="K",
    le_source="lehrer",
    leAe_source="lehrergeändert",
    ra_source="klassen",
    raAe_source="klassegeändert",
    kl_source="räume",
    target_source="klassen"
)