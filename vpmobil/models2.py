from __future__ import annotations
from dataclasses import dataclass, field, fields
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

    def as_dict(self) -> dict[str, Any]:
        """Gibt alle nicht versteckten Properties des Modells als Dictionary zurück und
        wandelt alle Datentypen in Primitives um, sodass das Dictionary beispielsweise
        in JSON modelliert werden kann.
        
        Verwendete Formate: 

        - `datetime(2025, 10, 18, 21, 3)` -> `"18.10.2025, 21:03"`
        - `time(21, 3)` -> `"21:03"`
        - `date(2025, 10, 18)` -> `"18.10.2025"`
        """

        converters = {
            datetime:        lambda d: d.strftime("%d.%m.%Y, %H:%M"),
            time:            lambda t: t.strftime("%H:%M"),
            date:            lambda d: d.strftime("%d.%m.%Y"),
            VpMobilPyModell: lambda m: m.as_dict(),
        }

        def apply_converter(value: Any) -> Any:
            if isinstance(value, list):
                return [apply_converter(v) for v in value]
            if isinstance(value, tuple):
                return list(apply_converter(v) for v in value)
            if isinstance(value, set):
                return list(apply_converter(v) for v in value)
            if isinstance(value, dict):
                return {k: apply_converter(v) for k, v in value.items()}

            for t, conv in converters.items():
                if isinstance(value, t):
                    return conv(value)

            return value

        result = {}

        for f in fields(self):
            name = f.name
            if not name.startswith("_"):
                result[name] = apply_converter(getattr(self, name))

        for name, attr in vars(self.__class__).items():
            if isinstance(attr, property) and not name.startswith("_"):
                result[name] = apply_converter(getattr(self, name))

        try: import json; _ = json.dumps(result, ensure_ascii=False)
        except: raise AssertionError(config.ERRORS.KEY_VALUE_ASSERTION)

        return result

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
        if (FreieTageTag := root.find("FreieTage")) is not None:
            freieTage = [
                datetime.strptime(ft.text, "%y%m%d").date()
                for ft in FreieTageTag.findall("ft")
                if ft.text is not None
            ]

        #======// Zusatzinfo //================//
        zusatzinfo = None
        if (ZusatzInfoTag := root.find('ZusatzInfo')) is not None:
            zusatzinfo = '\n'.join([
                ziZeile.text
                for ziZeile in ZusatzInfoTag.findall('ZiZeile')
                if ziZeile.text
            ])

        #======// Stunden, Aufsichten, Klausuren und Zeitplan //==//
        klausuren:  list[Klausur]  = []
        aufsichten: list[Aufsicht] = []
        stunden:    list[Stunde]   = []
        zeitplan:   dict[int, tuple[time | None, time | None]] = {}

        if (KlassenTag := root.find("Klassen")) is not None:
            for KlTag in KlassenTag.findall("Kl"):
                Kurz = find(KlTag, "Kurz", "text")

                if (KlausurenTag := KlTag.find("Klausuren")) is not None:
                    klausuren.extend([
                        Klausur.from_xml(KlausurTag)
                        for KlausurTag in KlausurenTag.findall("Klausur")
                    ])
                # Mergen macht für Klausuren meines Erachtens nach keinen Sinn
        
                if (AufsichtenTag := KlTag.find("Aufsichten")) is not None:
                    for AufsichtTag in AufsichtenTag.findall("Aufsicht"):
                        aufsicht = Aufsicht.from_xml(AufsichtTag, lehrer=[Kurz])
                                                
                        # Bekannte Aufsichten mergen
                        if (existing_aufsicht := next((a for a in aufsichten if a.beginn == aufsicht.beginn and a.ortinfo == aufsicht.ortinfo), None)):
                            existing_aufsicht.lehrer.update(aufsicht.lehrer)
                        else:
                            aufsichten.append(aufsicht)

                if (PlTag := KlTag.find("Pl")) is not None:
                    for StdTag in PlTag.findall("Std"):

                        stunde = Stunde.from_xml(StdTag, planart, kontext={Kurz})

                        # Bekannte Stunden mergen
                        if (existing_stunde := next((s for s in stunden if s.periode == stunde.periode and s.kursnummer == stunde.kursnummer and s.lehrer == stunde.lehrer), None)):
                            existing_stunde.klassen.update(stunde.klassen)
                            existing_stunde.räume.update(stunde.räume)
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
                if (KlStundenTag := KlTag.find("KlStunden")) is not None:
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
    
    def saveasfile(self, pfad: Path | str = "./datei.yml", overwrite=True) -> None:
        """Speichert den ausgewerteten Vertretungsplan als JSON- oder YAML-Datei.

        **ACHTUNG**: vpmobil-py hat momentan keine Funktion,
        um so abgespeicherte Dateien wieder einzulesen.

        Parameters:
            pfad (Path | str): Dateipfad der zu erstellenden Datei. Die Dateiendung bestimmt,
                welches Format gewählt wird. Unterstützt werden `.json` und `.yaml` (bzw. `.yml`).
                Andernfalls wird JSON gewählt.
            overwrite (bool): Ob die Datei überschrieben werden darf, falls sie bereits existiert

        Raises:
            FileExistsError: Falls die Datei bereits existiert und `overwrite` `False` ist
        """
        import yaml, json

        data = self.as_dict()

        zielpfad = Path(pfad).resolve() # Funktioniert für Path und str
        zielverzeichnis = zielpfad.parent
        zielverzeichnis.mkdir(parents=True, exist_ok=True)

        if zielpfad.exists() and not overwrite:
            raise FileExistsError(f"Datei '{zielpfad}' existiert bereits.")

        if zielpfad.suffix.lower() in ['.yaml', '.yml']:
            with zielpfad.open('w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        else:
            with zielpfad.open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    

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
    klassen:         set[str]    = field(default_factory=set)
    klassenänderung: bool        = field(default=False)
    lehrer:          set[str]    = field(default_factory=set)
    lehreränderung:  bool        = field(default=False)
    räume:           set[str]    = field(default_factory=set)
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
    def from_xml(cls, data: XML.Element, planart: Literal["K", "L", "R"] = "K", kontext: set[str] = set(), kontextgeändert: bool = False) -> Stunde:

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
        klassen = set()
        lehrer = set()
        räume = set()

        if planart == "K":
            klassen = kontext
            lehrer = set(Le.split(config.AUFZÄHLUNGS_SEPARATOR))  if fach else set()
            räume = set(Ra.split(config.AUFZÄHLUNGS_SEPARATOR))   if fach else set()
            klassenänderung = kontextgeändert
            lehreränderung = "LeAe" in find(data, "Le", "attrib")
            raumänderung = "RaAe" in find(data, "Ra", "attrib")
        elif planart == "L":
            klassen = set(Le.split(config.AUFZÄHLUNGS_SEPARATOR)) if fach else set()
            lehrer = kontext
            räume = set(Ra.split(config.AUFZÄHLUNGS_SEPARATOR))   if fach else set()
            klassenänderung = "LeAe" in find(data, "Le", "attrib")
            lehreränderung = kontextgeändert
            raumänderung = "RaAe" in find(data, "Ra", "attrib")
        elif planart == "R":
            klassen = set(Ra.split(config.AUFZÄHLUNGS_SEPARATOR)) if fach else set()
            lehrer = set(Le.split(config.AUFZÄHLUNGS_SEPARATOR))  if fach else set()
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
    lehrer:    set[str]    = field(default_factory=set)
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
    kurse:   set[str]         = field(default_factory=set)
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

        vp.saveasfile("test.yml")