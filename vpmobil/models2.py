from __future__ import annotations
from dataclasses import dataclass, field, InitVar
from xml.etree import ElementTree as XML
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Literal, Any, overload
import re

from vpmobil import config
from vpmobil.utils import slice_aufzählung

@dataclass(frozen=False)
class VpMobilPyModell:
    ...

    # def as_dict(self) -> dict[str, Any]:
    #     """Gibt alle nicht versteckten Properties des Modells als Dictionary zurück und
    #     wandelt alle Datentypen in Primitives um, sodass das Dictionary beispielsweise
    #     in JSON modelliert werden kann.
        
    #     Verwendete Formate: 

    #     - `datetime(2025, 10, 18, 21, 3)` -> `"18.10.2025, 21:03"`
    #     - `time(21, 3)` -> `"21:03"`
    #     - `date(2025, 10, 18)` -> `"18.10.2025"`
    #     """

    #     converters = {
    #         datetime:        lambda d: d.strftime("%d.%m.%Y, %H:%M"),
    #         time:            lambda t: t.strftime("%H:%M"),
    #         date:            lambda d: d.strftime("%d.%m.%Y"),
    #         VpMobilPyModell: lambda m: m.as_dict()
    #     }

    #     def apply_converter(value: Any) -> Any:
    #         if isinstance(value, list):
    #             return [apply_converter(v) for v in value]
    #         if isinstance(value, tuple):
    #             return list(apply_converter(v) for v in value)
    #         if isinstance(value, dict):
    #             return {k: apply_converter(v) for k, v in value.items()}

    #         for t, conv in converters.items():
    #             if isinstance(value, t):
    #                 return conv(value)

    #         return value

    #     result = {}
    #     for name in dir(self.__class__):
    #         if isinstance(getattr(self.__class__, name, None), property) and not name.startswith("_"):
    #             val = getattr(self, name)
    #             result[name] = apply_converter(val)

    #     try: import json; _ = json.dumps(result, ensure_ascii=False)
    #     except: raise AssertionError(config.ERRORS.KEY_VALUE_ASSERTION)

    #     return result

@overload
def find(element: XML.Element, path: str, mode: Literal["text"]) -> str | Literal[""]: ...
@overload
def find(element: XML.Element, path: str, mode: Literal["attrib"]) -> dict: ...
def find(element: XML.Element, path: str, mode: Literal["text", "attrib"]):
    target = element.find(path)
    if target is None:
        target = XML.Element(path.split('/')[-1])
    match mode:
        case "text":    return getattr(target, "text", "")
        case "attrib":  return getattr(target, "attrib", {})
        case _:         raise ValueError

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    Vertretungsplan                                       │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Vertretungsplan(VpMobilPyModell):
    datum:       date       | None                          = field(default=None)
    "Datum für das der Vertretungsplan gilt"
    datei:       str        | None                          = field(default=None)
    "Originaler Dateiname der Quelldatei"
    zeitstempel: datetime   | None                          = field(default=None)
    "Veröffentlichungszeitpunkt des Vertretungsplans bzw. der letzten Änderung"
    freieTage:   list[date]                                 = field(default_factory=list)
    "Unterrichtsfreie Tage"
    zusatzinfo:  str        | None                          = field(default=None)
    "Zusätzliche Informationen zum Tag. Kann mehrzeilig sein."
    zeitplan:    dict[int, tuple[time | None, time | None]] = field(default_factory=dict)
    """Die Unterrichtsperioden mit ihren Beginn- und Endzeiten. Die Schlüssel
    sind die Periodennummern, die Werte sind Tupel aus Beginn- und Endzeit.
    """
    stunden:     list[Stunde]                               = field(default_factory=list)
    aufsichten:  list[Aufsicht]                             = field(default_factory=list)
    klausuren:   list[Klausur]                              = field(default_factory=list)
    _planart:    Literal["K", "L", "R"] | None              = field(init=False, default="K")

    def __repr__(self):
        return f"<Vertretungsplan {f'(Typ {self._planart}) ' if self._planart else ""}vom {self.datum.strftime(r'%d.%m.%Y')}>"
    
    @classmethod # TODO
    def from_xml(cls, data: XML.Element | XML.ElementTree) -> Vertretungsplan:
        root = data if isinstance(data, XML.Element) else data.getroot()
        if root is None:
            raise ValueError

        import locale

        planart = find(root, "Kopf/planart", "text") or None
        
        #======// Datum //=====================//
        datum = None
        if DatumPlan := find(root, "Kopf/DatumPlan", "text"):
            for loc in ["de_DE.UTF-8", "German_Germany"]:
                try:
                    locale.setlocale(locale.LC_TIME, loc)
                    datum: date = datetime.strptime(DatumPlan, (r"%A, %d. %B %Y")).date()
                    break
                except: continue
            else:
                raise ValueError(f"Das Datum '{DatumPlan}' konnte nicht dekodiert werden. Bitte erstelle ein Issue im Bugtracker von vpmobil-py auf GitHub (https://github.com/annhilati/vpmobil-py/issues)")
        
        #======// Zeitstempel //===============//
        zeitstempel = None
        if s := find(root, "Kopf/zeitstempel", "text"):
            zeitstempel = datetime.strptime(s, r"%d.%m.%Y, %H:%M")

        #======// Freie Tage //================//
        freieTage = []
        if FreieTageTag := root.find("FreieTage"):
            freieTage = [
                datetime.strptime(ft.text, "%y%m%d").date()
                for ft in FreieTageTag.findall("ft")
                if ft.text is not None
            ]

        #======// Zusatzinfo //================//
        zusatzinfo = None
        if ZusatzInfoTag := root.find('ZusatzInfo'):
            zusatzinfo = '\n'.join([
                ziZeile.text
                for ziZeile in ZusatzInfoTag.findall('ZiZeile')
                if ziZeile.text
            ])

        #======// Stunden, Aufsichten, Klausuren und Zeitplan //==//
        klausuren:   list[Klausur]  = []
        aufsichten:  list[Aufsicht] = []
        zeitplan:    dict[int, tuple[time | None, time | None]] = {}
        stunden:     list[Stunde]   = []

        #                   TODO TODO TODO TODO TODO TODO

        if (KlassenTag := root.find("Klassen")):
            for KlTag in KlassenTag.findall("Kl"):
                Kurz = find(KlTag, "Kurz", "text")

                if KlausurenTag := KlTag.find("Klausuren"):
                    klausuren.extend([
                        Klausur.from_xml(KlausurTag)
                        for KlausurTag in KlausurenTag.findall("Klausur")
                    ])
                # Mergen macht für Klausuren meines Erachtens nach keinen Sinn
        
                if AufsichtenTag := KlTag.find("Aufsichten"):
                    for AufsichtTag in AufsichtenTag.findall("Aufsicht"):
                        aufsicht = Aufsicht.from_xml(AufsichtTag, lehrer=[Kurz])
                                                
                        # Bekannte Aufsichten mergen
                        if (existing_aufsicht := next((a for a in aufsichten if a.beginn == aufsicht.beginn and a.ortinfo == aufsicht.ortinfo), None)):
                            existing_aufsicht.lehrer.extend(aufsicht.lehrer)
                        else:
                            aufsichten.append(aufsicht)

                if (PlTag := KlTag.find("Pl")):
                    for StdTag in PlTag.findall("Std"):

                        stunde = Stunde.from_xml(StdTag, planart, kontext=[Kurz])

                        # Bekannte Stunden mergen
                        if (existing_stunde := next((s for s in stunden if s.periode == stunde.periode and s.kursnummer == stunde.kursnummer and s.lehrer == stunde.lehrer), None)):
                            existing_stunde.klassen.extend(stunde.klassen)
                            existing_stunde.räume.extend(stunde.räume)
                        else:
                            stunden.append(stunde)

                        # Zeitplan extrahieren
                        if stunde.periode in zeitplan:
                            beginn, ende = zeitplan[stunde.periode]
                            if beginn is None and stunde.beginn is not None:
                                beginn = stunde.beginn
                            if ende is None and stunde.ende is not None:
                                ende = stunde.ende
                            zeitplan[stunde.periode] = (beginn, ende)
                            continue
                        zeitplan[stunde.periode] = (stunde.beginn, stunde.ende)

                # Zeitplan ergänzen
                if (KlStundenTag := KlTag.find("KlStunden")):
                    for KlStTag in KlStundenTag.findall("KlSt"):
                        if not KlStTag.text or KlStTag.text in zeitplan or not KlStTag.attrib.get("ZeitVon") or not KlStTag.attrib.get("ZeitBis"):
                            continue
                        zeitplan[int(KlStTag.text)] = (
                            datetime.strptime(KlStTag.attrib.get("ZeitVon"), "%H:%M").time(),
                            datetime.strptime(KlStTag.attrib.get("ZeitBis"), "%H:%M").time()
                        )

        vp = Vertretungsplan(
            datum = datum,
            datei = find(root, "Kopf/datei", "text") or None,
            zeitstempel = zeitstempel,
            freieTage = freieTage,
            zusatzinfo = zusatzinfo,
            zeitplan = zeitplan,
            stunden = stunden,
            aufsichten = aufsichten,
            klausuren = klausuren
        )
        vp._planart = planart
        return vp
    

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Stunde                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Stunde(VpMobilPyModell):
    periode:         int
    beginn:          time | None = field(default=None)
    ende:            time | None = field(default=None)
    fach:            str  | None = field(default=None)
    fachänderung:    bool        = field(default=False)
    klassen:         list[str]   = field(default_factory=list)
    klassenänderung: bool        = field(default=False)
    lehrer:          list[str]   = field(default_factory=list)
    lehreränderung:  bool        = field(default=False)
    räume:           list[str]   = field(default_factory=list)
    raumänderung:    bool        = field(default=False)
    kursnummer:      int | None  = field(default=None)
    info:            str | None  = field(default=None)

    def __repr__(self):
        if self.ausfall:
            return f"<Ausfall: '{self.info}'>"
        return f"<\'{', '.join(self.klassen)}\' mit \'{self.fach}\' bei \'{', '.join(self.lehrer)}\' in \'{', '.join(self.räume)}\'>"
    
    @property
    def ausfall(self) -> bool:
        """Ob die Stunde entfällt.
        
        Wenn die Stundeninfo das Stichwort `"selbst"` enthält und weder Lehrer
        noch Räume angegeben sind, wird das ebenfalls als Ausfall interpretiert.
        """
        return self.fach is None or ("selbst" in (self.info or "") and not self.räume + self.lehrer)
    
    @classmethod
    def from_xml(cls, data: XML.Element, planart: Literal["K", "L", "R"] = "K", kontext: list[str] = [], kontextgeändert: bool = False) -> Stunde:

        beginn = None
        if s := find(data, "Beginn", "text"):
            beginn = datetime.strptime(s, "%H:%M").time()

        ende = None
        if s := find(data, "Ende", "text"):
            ende = datetime.strptime(s, "%H:%M").time()

        kursnummer = None
        if s := find(data, "Nr", "text"):
            kursnummer = int(s)

        #======// Fach & Änderungen bzw. Ausfall //==//
        Le = find(data, "Le", "text") or ""
        Ra = find(data, "Ra", "text") or ""

        fach = find(data, "Fa", "text") or None
        if fach == "---":
            fach = None
        # if "selbst" in fach and not Le and not Ra:
        #     fach = None # TODO: konkretisieren

        #======// Klassen, Lehrer & Räume //=========//
        klassen = []
        lehrer = []
        räume = []

        if planart == "K":
            klassen = kontext
            lehrer = Le.split(config.AUFZÄHLUNGS_SEPARATOR)  if fach else []
            räume = Ra.split(config.AUFZÄHLUNGS_SEPARATOR)   if fach else []
            klassenänderung = kontextgeändert
            lehreränderung = "LeAe" in find(data, "Le", "attrib")
            raumänderung = "RaAe" in find(data, "Ra", "attrib")
        elif planart == "L":
            klassen = Le.split(config.AUFZÄHLUNGS_SEPARATOR) if fach else []
            lehrer = kontext
            räume = Ra.split(config.AUFZÄHLUNGS_SEPARATOR)   if fach else []
            klassenänderung = "LeAe" in find(data, "Le", "attrib")
            lehreränderung = kontextgeändert
            raumänderung = "RaAe" in find(data, "Ra", "attrib")
        elif planart == "R":
            klassen = Ra.split(config.AUFZÄHLUNGS_SEPARATOR) if fach else []
            lehrer = Le.split(config.AUFZÄHLUNGS_SEPARATOR)  if fach else []
            räume = kontext
            klassenänderung = "RaAe" in find(data, "Ra", "attrib")
            lehreränderung = "LeAe" in find(data, "Le", "attrib")
            raumänderung = kontextgeändert

        return Stunde(
            periode = int(data.find("St").text),
            beginn = beginn,
            ende = ende,
            fach = fach,
            fachänderung = "FaAe" in find(data, "Fa", "attrib"),
            klassen=klassen,
            klassenänderung=klassenänderung,
            lehrer=lehrer,
            lehreränderung=lehreränderung,
            räume=räume,
            raumänderung=raumänderung,
            kursnummer = kursnummer,
            info = find(data, "If", "text") or None
        )


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                        Aufsicht                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Aufsicht(VpMobilPyModell):
    lehrer:    list[str]   = field(default_factory=list)
    vorStunde: int  | None = field(default=None)
    beginn:    time | None = field(default=None)
    zeitinfo:  str  | None = field(default=None)
    ortinfo:   str  | None = field(default=None)

    def __repr__(self):
        return f"<Aufsicht {f'von \'{", ".join(self.lehrer)}\' ' if self.lehrer else ""}{f'ab \'{self.beginn}\' - ' if self.beginn else "- "}{f'\'{self.ortinfo}\'' if self.ortinfo else ""}>"
    
    @classmethod
    def from_xml(cls, data: XML.Element, lehrer: list[str]) -> Aufsicht:

        vorStunde = None
        if s := find(data, "AuVorStunde", "text"):
            vorStunde = int(s)

        beginn = None
        if s := find(data, "AuUhrzeit", "text"):
            beginn = datetime.strptime(s, "%H:%M").time()

        return Aufsicht(
            lehrer=lehrer,
            vorStunde=vorStunde,
            beginn=beginn,
            zeitinfo=find(data, "AuZeit", "text") or None,
            ortinfo=find(data, "AuOrt", "text") or None,
        )


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Klausur                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Klausur(VpMobilPyModell): 
    kurse:   list[str]        = field(default_factory=list)
    lehrer:  str       | None = field(default=None)
    periode: int       | None = field(default=None)
    beginn:  time      | None = field(default=None)
    dauer:   timedelta | None = field(default=None)
    info:    str       | None = field(default=None)

    def __repr__(self):
        return f"<Klausur {f'für \'{", ".join(self.kurse)}\' ' if self.kurs else ""}{f'ab \'{self.beginn}\'' if self.beginn else ""}>"
    
    @classmethod
    def from_xml(cls, data: XML.Element) -> Klausur:

        periode = None
        if s := find(data, "KlStunde", "text"):
            periode = int(s)

        beginn = None
        if s := find(data, "KlBeginn", "text"):
            beginn = datetime.strptime(s, "%H:%M").time()

        dauer = None
        if s := find(data, "KlDauer", "text"):
            dauer = timedelta(minutes=int(s))

        return Klausur(
            kurse=slice_aufzählung(find(data, "KlKurs", "text")) or None,
            lehrer=find(data, "KlKursleiter", "text") or None,
            periode=periode,
            beginn=beginn,
            dauer=dauer,
            info=find(data, "KlKinfo", "text") or None
        )


if __name__ == "__main__":
    with open(r"C:\Users\Annhilati\Documents\GitHub\dof-shaderpack\vpmobil-py\analyse\PlanKl20250811.xml", "r", encoding="utf-8") as f:
        vp = Vertretungsplan.from_xml(XML.parse(f))

        print(vp)
        [print(s) for s in vp.stunden]
        print(vp.zeitplan)