from __future__ import annotations
from dataclasses import dataclass, field, fields
from xml.etree import ElementTree as XML
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Literal, Any
import re

from vpmobil import config
from vpmobil.utils import slice_aufzählung, find

@dataclass(frozen=False)
class VpMobilPyModell:

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
    kurse:       list[Kurs]                                 = field(default_factory=list)
    stunden:     list[Stunde]                               = field(default_factory=list)
    aufsichten:  list[Aufsicht]                             = field(default_factory=list)
    klausuren:   list[Klausur]                              = field(default_factory=list)
    _planart:    Literal["K", "L", "R"] | None              = field(init=False, default="K")

    def __repr__(self):
        return f"<Vertretungsplan {f'(Typ {self._planart}) ' if self._planart else ""}vom {self.datum.strftime(r'%d.%m.%Y')}>"
    
    @property
    def klassen(self) -> dict[str, Klasse]:
        "Im Vertretungsplan beschriebene Klassen"

        klassen: dict[str, Klasse] = {}
        for stunde in self.stunden:
            for klasse in stunde.klassen:
                if klasse not in klassen:
                    klassen[klasse] = Klasse(kürzel=klasse)
                if stunde.periode not in klassen[klasse].stunden:
                    klassen[klasse].stunden[stunde.periode] = []
                klassen[klasse].stunden[stunde.periode].append(stunde)

        for kurs in self.kurse:
            for klasse in kurs.klassen:
                if klasse not in klassen:
                    klassen[klasse] = Klasse(kürzel=klasse)
                klassen[klasse].kurse[kurs.kursnummer] = kurs

        for klausur in self.klausuren:
            for kurs in klausur.kurse:
                for klasse in self.klassen.get(kurs, Klasse()).stunden:
                    if klasse not in klassen:
                        klassen[klasse] = Klasse(kürzel=klasse)
                    klassen[klasse].klausuren.append(klausur)

        return dict(sorted(klassen.items()))
    
    @property
    def lehrer(self) -> dict[str, Lehrer]:
        "Im Vertretungsplan beschriebene Lehrer"
        
        lehrerE: dict[str, Lehrer] = {}
        for stunde in self.stunden:
            for klasse in stunde.räume:
                if klasse not in lehrerE:
                    lehrerE[klasse] = Lehrer(kürzel=klasse)
                if stunde.periode not in lehrerE[klasse].stunden:
                    lehrerE[klasse].stunden[stunde.periode] = []
                lehrerE[klasse].stunden[stunde.periode].append(stunde)

        for kurs in self.kurse:
            lehrer = kurs.lehrer or ""
            if lehrer not in lehrerE:
                lehrerE[lehrer] = Lehrer(kürzel=lehrer)
            lehrerE[lehrer].kurse[kurs.kursnummer] = kurs

        return dict(sorted(lehrerE.items()))
    
    @property
    def räume(self) -> dict[str, Raum]:
        "Im Vertretungsplan beschriebene Räume"
        
        räumeE: dict[str, Raum] = {}
        for stunde in self.stunden:
            for raum in stunde.räume:
                if raum not in räumeE:
                    räumeE[raum] = Raum(kürzel=raum)
                if stunde.periode not in räumeE[raum].stunden:
                    räumeE[raum].stunden[stunde.periode] = []
                räumeE[raum].stunden[stunde.periode].append(stunde)

        return dict(sorted(räumeE.items()))

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
        kurse:      list[Kurs]     = []
        klausuren:  list[Klausur]  = []
        aufsichten: list[Aufsicht] = []
        stunden:    list[Stunde]   = []
        zeitplan:   dict[int, tuple[time | None, time | None]] = {}

        if (KlassenTag := root.find("Klassen")) is not None:
            for KlTag in KlassenTag.findall("Kl"):
                Kurz = find(KlTag, "Kurz", "text")

                # Klausuren auswerten
                if (KlausurenTag := KlTag.find("Klausuren")) is not None:
                    klausuren.extend([
                        Klausur.from_xml(KlausurTag)
                        for KlausurTag in KlausurenTag.findall("Klausur")
                    ])
        
                # Aufsichten auswerten
                if (AufsichtenTag := KlTag.find("Aufsichten")) is not None:
                    for AufsichtTag in AufsichtenTag.findall("Aufsicht"):
                        aufsicht = Aufsicht.from_xml(AufsichtTag, lehrer=[Kurz])
                                                
                        # Bekannte Aufsichten mergen
                        if (existing_aufsicht := next((a for a in aufsichten if a.beginn == aufsicht.beginn and a.ortinfo == aufsicht.ortinfo), None)):
                            existing_aufsicht.lehrer.update(aufsicht.lehrer)
                        else:
                            aufsichten.append(aufsicht)

                # Stunden auswerten
                if (PlTag := KlTag.find("Pl")) is not None:
                    for StdTag in PlTag.findall("Std"):

                        stunde = Stunde.from_xml(StdTag, planart, kontext={Kurz})

                        # Bekannte Stunden mergen
                        if (existing_stunde := next((s for s in stunden if s.periode == stunde.periode and s.kursnummer == stunde.kursnummer and s.räume == stunde.räume), None)):
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

                # Kurse auswerten
                if (UnterrichtsTag := KlTag.find("Unterricht")) is not None:
                    for UeTag in UnterrichtsTag.findall("Ue"):
                        kurs = Kurs.from_xml(UeTag, klassen={Kurz})

                        # Bekannte Stunden mergen
                        if (existing_kurs := next((k for k in kurse if k.kursnummer == kurs.kursnummer), None)):
                            existing_kurs.klassen.update(kurs.klassen)
                        else:
                            kurse.append(kurs)

        vp = Vertretungsplan(
            datum = datum,
            datei = find(root, "Kopf/datei", "text") or None,
            zeitstempel = zeitstempel,
            freieTage = freieTage,
            zusatzinfo = zusatzinfo,
            zeitplan = zeitplan,
            kurse = sorted(kurse, key=lambda kurs: (kurs.kursnummer is None, kurs.kursnummer)),
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
    "Unterrichtsperiode der Stunde. Kann `0` sein."
    beginn:          time | None = field(default=None)
    "Beginn der Stunde. Falls keine Uhrzeit angegeben ist, sollte `VertretungsTag.zeitplan` zu Rate gezogen werden."
    ende:            time | None = field(default=None)
    "Ende der Stunde. Falls keine Uhrzeit angegeben ist, sollte `VertretungsTag.zeitplan` zu Rate gezogen werden."
    fach:            str  | None = field(default=None)
    """Fach bzw. Kürzel des Kurses der Stunde. Gibt `None` zurück, wenn die Stunde entfällt.

    Das tatsächlich gängige Kürzel des Fachs kann über
    `klasse.kurs(stunde.kursnummer).fach` erhalten werden.

    Bei Unsicherheit mit Fallback wäre beispielsweise denkbar:
    ```
    stunde.fach if klasse.kurse[stunde.kursnummer] is None else klasse.kurse[stunde.kursnummer].fach
    ```
    """
    fachmeta:        str | None  = field(default=None)
    """Metainformation über das Fach das normalerweise in dieser Stunde stattfindet.

    Das Verhalten dieses Werts ist etwas unintuitiv. Er wird hauptsächlich bei
    Stunden von Kursen gesetzt, die mehrere inhatlich parallele Gruppen haben,
    beispielsweise bei Sport (wenn es separate Kurse für Jungen und Mädchen gibt),
    Profilen, Religionsgruppen und Kursen der Oberstufe generell.
    
    Dieser Wert ist bei entsprechenden Stunden immer gesetzt, auch wenn die Stunde
    entfällt oder das Fach geändert wurde.
    """
    fachänderung:    bool        = field(default=False)
    "Ob das Fach der Stunde geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt."
    klassen:         set[str]    = field(default_factory=set)
    "Alle Klassen der Stunde. Gibt `[]` zurück, wenn die Stunde entfällt oder keine Klassen eingetragen sind."
    klassenänderung: bool        = field(default=False)
    "Ob die Klassen der Stunde geändert wurden. Ebenfalls `True`, wenn die Stunde entfällt."
    lehrer:          set[str]    = field(default_factory=set)
    "Alle Lehrer der Stunde. Gibt `[]` zurück, wenn die Stunde entfällt oder keine Lehrer eingetragen sind."
    lehreränderung:  bool        = field(default=False)
    "Ob die Lehrer der Stunde geändert wurden. Ebenfalls `True`, wenn die Stunde entfällt."
    räume:           set[str]    = field(default_factory=set)
    "Alle Räume der Stunde. Gibt `[]` zurück, wenn die Stunde entfällt oder keine Räume eingetragen sind."
    raumänderung:    bool        = field(default=False)
    "Ob der Raum der Stunde geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt."
    kursnummer:      int | None  = field(default=None)
    """Nummer des Kurses der Stunde

    Kann `None` sein, wenn das Fach der Stunde geändert wurde, jedoch nicht, wenn
    die Stunde entfällt oder, beispielsweise wenn die Stunde eine Exkursion ist.
    
    Kursnummern können verwendet werden, um in den Kursen einer Klasse mehr
    Details zu einem Kurs zu erhalten, beispielsweise wenn eine Unterrichtsstunde
    ausfällt und Informationen wie Lehrer, Fach und Raum deswegen nicht verfügbar sind.
    """
    info:            str | None  = field(default=None)
    "Zusätzliche Informationen zur Stunde"

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
        return self.fach is None or ("selbst" in (self.info or "") and not self.lehrer | self.räume)
    
    @property
    def änderung(self) -> bool:
        "Ob die Stunde in irgendeiner Weise geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt"
        return self.fachänderung or self.lehreränderung or self.raumänderung or self.klassenänderung
    
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
            if s.endswith("+"): # Gemäß #44
                s = s[:-1]
            kursnummer = int(s)

        #======// Fach & Änderungen bzw. Ausfall //==//
        Le = find(data, "Le", "text") or ""
        Ra = find(data, "Ra", "text") or ""

        fach = find(data, "Fa", "text") or None
        if fach == "---":
            fach = None

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
            fachmeta= find(data, "Ku2", "text") or None,
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
# │                                          Kurs                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Kurs(VpMobilPyModell):
    """Klasse die einen bestimmten Kurs repräsentiert.
    """
    kursnummer: int | None
    "Kursnummer des Kurses"
    kürzel:     str | None = field(default=None)
    "Gruppenbezeichnung des Kurses. Falls in den Quelldaten nicht vorhanden, wird stattdessen das Fach zurückgegeben."
    fach:       str | None = field(default=None)
    "Fach des Kurses"
    lehrer:     str | None = field(default=None)
    "Lehrer des Kurses"
    klassen:    set[str]   = field(default_factory=set)

    @classmethod
    def from_xml(cls, data: XML.Element, klassen: set[str]) -> Kurs:
        return Kurs(
            kursnummer = int(find(data, "UeNr", "text")) if find(data, "UeNr", "text") else None,
            kürzel = find(data, "UeNr", "attrib").get("UeGr", None) or find(data, "UeNr", "attrib").get("UeFa", None),
            fach = find(data, "UeNr", "attrib").get("UeFa", None),
            lehrer = find(data, "UeNr", "attrib").get("UeLe", None),
            klassen = klassen
        )

    def __repr__(self) -> str:
        return f"<'{self.kürzel}' bei '{self.lehrer}' (Kursnummer '{self.kursnummer}')>"


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                        Aufsicht                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Aufsicht(VpMobilPyModell):
    lehrer:    set[str]    = field(default_factory=set)
    vorStunde: int  | None = field(default=None)
    "Unterrichtsperiode, vor der die Aufsicht stattfindet"
    beginn:    time | None = field(default=None)
    "Uhrzeit der Aufsicht"
    zeitinfo:  str  | None = field(default=None)
    "Hinweis zum Zeitpunkt der Aufsicht"
    ortinfo:   str  | None = field(default=None)
    "Hinweis zum Ort der Aufsicht"

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


@dataclass(frozen=False)
class ViewBase(VpMobilPyModell):
    kürzel: str
    stunden: dict[int, list[Stunde]] = field(default_factory=dict)
    "Stunden gruppiert nach Unterrichtsperiode"


@dataclass(frozen=False)
class Klasse(ViewBase):
    kurse: dict[int, Kurs]   = field(default_factory=dict)
    "Kurse der Klasse, zugänglich über die Kursnummer"
    klausuren: list[Klausur] = field(default_factory=list)
    "Klausuren der Klasse"

    def __repr__(self):
        return f"<Klasse '{self.kürzel}'>"

@dataclass(frozen=False)
class Lehrer(ViewBase):
    kurse: dict[int, Kurs]     = field(default_factory=dict)
    "Kurse des Lehrers, zugänglich über die Kursnummer"
    aufsichten: list[Aufsicht] = field(default_factory=list)
    "Aufsichten des Lehrers"

    def __repr__(self):
        return f"<Lehrer '{self.kürzel}'>"

@dataclass(frozen=False)
class Raum(ViewBase):

    def __repr__(self):
        return f"<Raum '{self.kürzel}'>"


if __name__ == "__main__":
    with open(r"C:\Users\Annhilati\Documents\GitHub\dof-shaderpack\vpmobil-py\analyse\PlanKl20250811.xml", "r", encoding="utf-8") as f:
        vp = Vertretungsplan.from_xml(XML.parse(f))

        print(vp.klassen)
        print(vp.lehrer)
        print(vp.räume)