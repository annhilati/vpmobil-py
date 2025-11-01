"""Erweiterung zum Umwandeln von Vertretungsplan-Datenmodellen

---

Mit den Funktionen dieses Submoduls können Vertretungsplantag in eine andere Planart umgewandelt werden.

So können beispielsweise `KlassenVertretungsTag`-Objekte (mit geringfügigen Einbußen) in `LehrerVertretungsTag`-Objekte umgewandelt werden,
um so eine Auswertung aus Perspektive der Lehrer zu ermöglichen.
"""

from typing import Callable, Literal
from vpmobil.models import (
    KlassenVertretungsTag, LehrerVertretungsTag, RaumVertretungsTag, VertretungsTag,
    Stunde, Kurs,
    VertretungsTagType, KlasseLikeType
)
from vpmobil import config
import xml.etree.ElementTree as XML

def _converter(
    planart:       Literal["K", "L", "R"],
    get_Le:        Callable[[Stunde], list[str]],
    get_LeAe:      Callable[[Stunde], bool],
    get_Ra:        Callable[[Stunde], list[str]],
    get_RaAe:      Callable[[Stunde], bool],
    get_old_Kl:    Callable[[VertretungsTagType], dict[str, KlasseLikeType]],
    get_Kl_target: Callable[[Stunde], list[str]],
    get_Kl_target_K: Callable[[Kurs], str]
):
    def _subElement(parent: XML.Element, tag: str, text: str = None, attrib: dict = {}) -> XML.Element:
        element = XML.SubElement(parent, tag, attrib)
        if text:
            element.text = text
        return element

    def converter(tag: VertretungsTagType):
        root = XML.Element("VpMobil")

        Kopf = _subElement(root, "Kopf")
        _subElement(Kopf, "planart", planart)
        _subElement(Kopf, "zeitstempel", tag.zeitstempel.strftime("%d.%m.%Y, %H:%M"))
        _subElement(Kopf, "DatumPlan", tag.datum.strftime("%A, %d. %B %Y"))

        FreieTage = _subElement(root, "FreieTage")
        for datum in tag.freieTage:
            _subElement(FreieTage, "ft", datum.strftime("%y%m%d"))

        Klassen = _subElement(root, "Klassen")
        merge_map: dict[str, dict[tuple, dict[str, set[str]]]] = {}

        for klasseLike in get_old_Kl(tag).values():
            for periode, stunden in klasseLike.stunden.items():
                for stunde in stunden:

                    targets = (
                        get_Kl_target(stunde)
                        or ([get_Kl_target_K(klasseLike.kurse[stunde.kursnummer])]
                            if getattr(klasseLike, "kurs", None)
                            and stunde.kursnummer is not None
                            and get_Kl_target_K(klasseLike.kurse[stunde.kursnummer]) is not None
                            else [])
                    )

                    for target in targets:
                        key = (
                            target,
                            stunde.periode,
                            stunde.fach or "",
                            getattr(stunde, "kursnummer", None),
                            getattr(stunde, "info", None),
                            stunde.beginn.strftime("%H:%M") if stunde.beginn else "",
                            stunde.ende.strftime("%H:%M") if stunde.ende else "",
                        )

                        merge_map.setdefault(target, {})
                        if key not in merge_map[target]:
                            merge_map[target][key] = {"Le": set(), "Ra": set(), "LeAe": False, "RaAe": False, "fachgeändert": stunde.fachgeändert, "ausfall": stunde.ausfall}

                        merge_map[target][key]["Le"].update(get_Le(stunde))
                        merge_map[target][key]["Ra"].update(get_Ra(stunde))
                        merge_map[target][key]["LeAe"] |= bool(get_LeAe(stunde))
                        merge_map[target][key]["RaAe"] |= bool(get_RaAe(stunde))

        # XML erzeugen
        for target, stunden_dict in merge_map.items():
            Kl = _subElement(Klassen, "Kl")
            _subElement(Kl, "Kurz", target)
            Pl = _subElement(Kl, "Pl")

            for (target, periode, fach, kursnummer, info, beginn, ende), vals in sorted(stunden_dict.items(), key=lambda x: int(x[0][1])):
                Std = _subElement(Pl, "Std")
                _subElement(Std, "St", str(periode))
                if beginn:
                    _subElement(Std, "Beginn", beginn)
                if ende:
                    _subElement(Std, "Ende", ende)

                fa_text = "" if fach is None and not vals["ausfall"] else fach if not vals["ausfall"] else "---"
                Fa = _subElement(Std, "Fa", fa_text)
                if vals["fachgeändert"]:
                    Fa.set("FaAe", "FaGeaendert")

                Le = _subElement(Std, "Le", config.AUFZÄHLUNGS_SEPARATOR.join(sorted(vals["Le"])))
                if vals["LeAe"]:
                    Le.set("LeAe", "LeGeaendert")

                Ra = _subElement(Std, "Ra", config.AUFZÄHLUNGS_SEPARATOR.join(sorted(vals["Ra"])))
                if vals["RaAe"]:
                    Ra.set("RaAe", "RaGeaendert")

                if kursnummer:
                    _subElement(Std, "Nr", str(kursnummer))
                if info:
                    _subElement(Std, "If", info)

        Klassen[:] = sorted(Klassen, key=lambda e: e.findtext("Kurz"))

        return VertretungsTag(XML.ElementTree(root))

    return converter



def KlassenPerspektive(tag: LehrerVertretungsTag | RaumVertretungsTag, /) -> KlassenVertretungsTag:
    """Wandelt einen Vertretungsplan in einen aus der Perspektive der Klassen um.
    
    Verloren gehen
    --------
    - Dateiname
    - Aufsichten
    """
    if type(tag) == LehrerVertretungsTag:
        return _converter(
            planart=     "K",
            get_Le=       lambda s: s.lehrer,
            get_LeAe=     lambda s: s.lehrergeändert,
            get_Ra=       lambda s: s.räume,
            get_RaAe=     lambda s: s.raumgeändert,
            get_old_Kl=   lambda d: d.lehrer,
            get_Kl_target=lambda s: s.klassen,
            get_Kl_target_K=lambda s: None
        )(tag)
    elif type(tag) == RaumVertretungsTag:
        return _converter(
            planart=     "K",
            get_Le=       lambda s: s.lehrer,
            get_LeAe=     lambda s: s.lehrergeändert,
            get_Ra=       lambda s: s.räume,
            get_RaAe=     lambda s: s.raumgeändert,
            get_old_Kl=   lambda d: d.räume,
            get_Kl_target=lambda s: s.klassen,
            get_Kl_target_K=lambda k: None
        )(tag)
    elif type(tag) == KlassenVertretungsTag:
        return tag
    else:
        raise ValueError(f"Unzulässiger Plantyp: {type(tag)}")

def LehrerPerspektive(tag: KlassenVertretungsTag | RaumVertretungsTag, /) -> LehrerVertretungsTag:
    """Wandelt einen Vertretungsplan in einen aus der Perspektive der Lehrer um.
    
    Verloren gehen
    --------
    - Dateiname
    - Kurse
    - Klausuren
    """

    if type(tag) == KlassenVertretungsTag:
        return _converter(
            planart=     "L",
            get_Le=       lambda s: s.klassen,
            get_LeAe=     lambda s: s.klassegeändert,
            get_Ra=       lambda s: s.räume,
            get_RaAe=     lambda s: s.raumgeändert,
            get_old_Kl=   lambda d: d.klassen,
            get_Kl_target=lambda s: s.lehrer,
            get_Kl_target_K=lambda k: k.lehrer
        )(tag)
    elif type(tag) == RaumVertretungsTag:
        return _converter(
            planart=     "L",
            get_Le=       lambda s: s.klassen,
            get_LeAe=     lambda s: s.klassegeändert,
            get_Ra=       lambda s: s.räume,
            get_RaAe=     lambda s: s.raumgeändert,
            get_old_Kl=   lambda d: d.räume,
            get_Kl_target=lambda s: s.lehrer,
            get_Kl_target_K=lambda k: None
        )(tag)
    elif type(tag) == LehrerVertretungsTag:
        return tag
    else:
        raise ValueError(f"Unzulässiger Plantyp: {type(tag)}")
    
def RaumPerspektive(tag: KlassenVertretungsTag | LehrerVertretungsTag, /) -> RaumVertretungsTag:
    """Wandelt einen Vertretungsplan in einen aus der Perspektive der Klassen um.
    
    Verloren gehen
    --------
    - Dateiname
    - Aufsichten
    - Kurse
    - Klausuren
    """

    if type(tag) == KlassenVertretungsTag:
        return _converter(
            planart=     "R",
            get_Le=       lambda s: s.lehrer,
            get_LeAe=     lambda s: s.lehrergeändert,
            get_Ra=       lambda s: s.klassen,
            get_RaAe=     lambda s: s.klassegeändert,
            get_old_Kl=   lambda d: d.klassen,
            get_Kl_target=lambda s: s.räume,
            get_Kl_target_K=lambda k: None
        )(tag)
    elif type(tag) == LehrerVertretungsTag:
        return _converter(
            planart=     "R",
            get_Le=       lambda s: s.lehrer,
            get_LeAe=     lambda s: s.lehrergeändert,
            get_Ra=       lambda s: s.klassen,
            get_RaAe=     lambda s: s.klassegeändert,
            get_old_Kl=   lambda d: d.lehrer,
            get_Kl_target=lambda s: s.räume, 
            get_Kl_target_K=lambda k: None
        )(tag)
    elif type(tag) == RaumVertretungsTag:
        return tag
    else:
        raise ValueError(f"Unzulässiger Plantyp: {type(tag)}")