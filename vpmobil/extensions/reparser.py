"""Dieses Erweiterungsmodul enthält Funktionen, um Vertretungspläne so
umzuwandeln, dass Auswertung auch aus Perspektive von Lehrern oder Räumen
möglich ist.
"""

# Die Implementierung hier ist noch ziemlich unschön, aber sie funktioniert.
# Das Hauptproblem ist die merge_map, die dafür sorgt, dass Stunden, die in
# verschiedenen Klassenplänen auftauchen, zusammengefasst werden.


from typing import Callable, Literal
from vpmobil.models import (
    KlassenVertretungsTag, LehrerVertretungsTag, RaumVertretungsTag, VertretungsTag,
    Stunde, Kurs, Klasse, Lehrer, Raum
)
from vpmobil import config
import xml.etree.ElementTree as XML

type VertretungsTagType = KlassenVertretungsTag | RaumVertretungsTag | LehrerVertretungsTag
type KlasseLikeType = Klasse | Lehrer | Raum

def _converter_fabric(
    planart:       Literal["K", "L", "R"],
    get_Le:        Callable[[Stunde], list[str]],
    get_LeAe:      Callable[[Stunde], bool],
    get_Ra:        Callable[[Stunde], list[str]],
    get_RaAe:      Callable[[Stunde], bool],
    get_old_Kl:    Callable[[VertretungsTagType], dict[str, KlasseLikeType]],
    get_Kl_target: Callable[[Stunde], list[str]],
    get_Kl_target_K: Callable[[Kurs], str]
):
    def add_Element(parent: XML.Element, tag: str, text: str = None, attrib: dict = {}) -> XML.Element:
        element = XML.SubElement(parent, tag, attrib)
        if text:
            element.text = text
        return element

    def converter(tag: VertretungsTagType):
        root = XML.Element("VpMobil")

        Kopf = add_Element(root, "Kopf")
        add_Element(Kopf, "planart", planart)
        add_Element(Kopf, "zeitstempel", tag.zeitstempel.strftime("%d.%m.%Y, %H:%M"))
        add_Element(Kopf, "DatumPlan", tag.datum.strftime("%A, %d. %B %Y"))

        FreieTage = add_Element(root, "FreieTage")
        for datum in tag.freieTage:
            add_Element(FreieTage, "ft", datum.strftime("%y%m%d"))

        Klassen = add_Element(root, "Klassen")
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
            Kl = add_Element(Klassen, "Kl")
            add_Element(Kl, "Kurz", target)
            Pl = add_Element(Kl, "Pl")

            for (target, periode, fach, kursnummer, info, beginn, ende), vals in sorted(stunden_dict.items(), key=lambda x: int(x[0][1])):
                Std = add_Element(Pl, "Std")
                add_Element(Std, "St", str(periode))
                if beginn:
                    add_Element(Std, "Beginn", beginn)
                if ende:
                    add_Element(Std, "Ende", ende)

                fa_text = "" if fach is None and not vals["ausfall"] else fach if not vals["ausfall"] else "---"
                Fa = add_Element(Std, "Fa", fa_text)
                if vals["fachgeändert"]:
                    Fa.set("FaAe", "FaGeaendert")

                Le = add_Element(Std, "Le", config.AUFZÄHLUNGS_SEPARATOR.join(sorted(vals["Le"])))
                if vals["LeAe"]:
                    Le.set("LeAe", "LeGeaendert")

                Ra = add_Element(Std, "Ra", config.AUFZÄHLUNGS_SEPARATOR.join(sorted(vals["Ra"])))
                if vals["RaAe"]:
                    Ra.set("RaAe", "RaGeaendert")

                if kursnummer:
                    add_Element(Std, "Nr", str(kursnummer))
                if info:
                    add_Element(Std, "If", info)

        Klassen[:] = sorted(Klassen, key=lambda e: e.findtext("Kurz"))

        return VertretungsTag(XML.ElementTree(root))

    return converter



def KlassenPerspektive(tag: VertretungsTag, /) -> KlassenVertretungsTag:
    """Wandelt einen Vertretungsplan in einen aus der Perspektive der Klassen
    um. Dateiname und Lehreraufsichten gehen verloren.
    """
    if type(tag) == LehrerVertretungsTag:
        return _converter_fabric(
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
        return _converter_fabric(
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
        raise ValueError(f"Unbekannter Plantyp: {type(tag)}")

def LehrerPerspektive(tag: VertretungsTag, /) -> LehrerVertretungsTag:
    """Wandelt einen Vertretungsplan in einen aus der Perspektive der Lehrer
    um. Dateiname, Kurse und Klausuren gehen verloren.
    """

    if type(tag) == KlassenVertretungsTag:
        return _converter_fabric(
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
        return _converter_fabric(
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
        raise ValueError(f"Unbekannter Plantyp: {type(tag)}")
    
def RaumPerspektive(tag: VertretungsTag, /) -> RaumVertretungsTag:
    """Wandelt einen Vertretungsplan in einen aus der Perspektive der Räume
    um. Veloren gehen Dateiname, Lehreraufsichten, Kurse und Klausuren.
    """

    if type(tag) == KlassenVertretungsTag:
        return _converter_fabric(
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
        return _converter_fabric(
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
        raise ValueError(f"Unbekannter Plantyp: {type(tag)}")