from __future__ import annotations
from dataclasses import dataclass, field, fields
from xml.etree import ElementTree as XML
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Literal, Any, ClassVar
from types import MappingProxyType
import copy

from vpmobil.utils import find, ElementBuilder, prettyxml, Mapping, Collection, natural_sort_key
from vpmobil.parser import Parser

@dataclass(frozen=False)
class VpMobilPyModell:
    _hidden: ClassVar[list[str]] = []

    def as_dict(self, hidden: list[str] = []) -> dict[str, Any]:
        """Gibt alle nicht versteckten Felder und Properties des Modells als Dictionary
        zurück und wandelt alle Datentypen in Primitives um, sodass das Dictionary
        beispielsweise in JSON modelliert werden kann.
        
        Verwendete Formate: 

        - `datetime(2025, 10, 18, 21, 3)` -> `"18.10.2025, 21:03"`
        - `time(21, 3)` -> `"21:03"`
        - `date(2025, 10, 18)` -> `"18.10.2025"`
        - `("A", "B")` -> `["A", "B"]`
        - `{"A", "B"}` -> `["A", "B"]`
        """

        converters = {
            VpMobilPyModell:  lambda m: m.as_dict(hidden=hidden),
            datetime:         lambda d: d.strftime("%d.%m.%Y, %H:%M"),
            time:             lambda t: t.strftime("%H:%M"),
            date:             lambda d: d.strftime("%d.%m.%Y"),
            list:             lambda l: [apply_converter(v) for v in l],
            tuple:            lambda t: [apply_converter(v) for v in t],
            set:              lambda s: [apply_converter(v) for v in s],
            dict:             lambda d: {k: apply_converter(v) for k, v in d.items()},
            MappingProxyType: lambda m: {k: apply_converter(v) for k, v in m.items()}
        }

        def apply_converter(value: Any) -> Any:
            for t, conv in converters.items():
                if isinstance(value, t):
                    return conv(value)

            return value

        result = {}

        for f in fields(self):
            name = f.name
            if not name.startswith("_") and name not in self._hidden + hidden:
                result[name] = apply_converter(getattr(self, name))

        for name, attr in vars(self.__class__).items():
            if isinstance(attr, property) and not name.startswith("_") and name not in self._hidden + hidden:
                result[name] = apply_converter(getattr(self, name))

        try:
            import json; json.dumps(result, ensure_ascii=False)
        except Exception as e:
            raise AssertionError(f"Die Konvertierung des Datenmodells ist fehlgeschlagen. ({e}) Melde diesen Fall unbedingt auf GitHub im Bugtracker von vpmobil-py")

        return result

    def __deepcopy__(self, memo):
        result = self.__class__.__new__(self.__class__)
        memo[id(self)] = result

        for feld in fields(self):
            value = getattr(self, feld.name)

            if isinstance(value, MappingProxyType):
                copied = copy.deepcopy(dict(value), memo)
                copied = MappingProxyType(copied)
            else:
                copied = copy.deepcopy(value, memo)

            setattr(result, feld.name, copied)

        return result
    
    def __copy__(self):
        result = self.__class__.__new__(self.__class__)

        for feld in fields(self):
            value = getattr(self, feld.name)

            if isinstance(value, MappingProxyType):
                copied = MappingProxyType(dict(value))
            else:
                copied = copy.copy(value)

            setattr(result, feld.name, copied)

        return result
    
    def copy(self):
        """Erzeugt eine neue identische Instanz. Auch der Inhalt der Felder werden
        kopiert. Falls dies nicht erwünscht ist, nutze `~.__copy__()` bzw. `copy.copy()`.
        """
        return self.__deepcopy__(None)
    

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    Vertretungsplan                                       │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Vertretungsplan(VpMobilPyModell):
    """`Vertretungsplan` ist die einheitliche Klasse für die Vertretungsplan-Daten eines Tages.
    
    Ein `Vertretungsplan`-Objekt kann über `~.from_xml()` aus XML-Quelldaten erzeugt werden.
    """
    
    datum:       date       | None                          = field(default=None)
    "Datum für das der Vertretungsplan gilt"
    dateiname:   str        | None                          = field(default=None)
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
    "Globales Reservoir für Kurse"
    stunden:     list[Stunde]                               = field(default_factory=list)
    """Globales Reservoir für Stunden.
    
    **ACHTUNG**: Auf dieser Liste sollte nicht operiert werden, um
    das Entstehen von Redundanzen zu vermeiden.
    """
    aufsichten:  list[Aufsicht]                             = field(default_factory=list)
    "Globales Reservoir für Aufsichten"
    klausuren:   list[Klausur]                              = field(default_factory=list)
    "Globales Reservoir für Klausuren"
    _planart:    Literal["K", "L", "R"] | None              = field(init=False, default="K")
    _hidden:     ClassVar[list[str]]                        = ["kurse", "stunden", "aufsichten", "klausuren"]

    def __repr__(self):
        return "<" + " ".join(filter(None, [
            "Vertretungsplan",
            f"(Typ {self._planart})" if self._planart else "",
            f"vom {self.datum.strftime(r'%d.%m.%Y')}" if self.datum else ""
        ])) + ">"
    
    def __getitem__(self, key) -> Klasse | Lehrer | Raum:
        if key in self.klassen: 
            return self.klassen[key]
        elif key in self.lehrer: 
            return self.lehrer[key]
        elif key in self.räume: 
            return self.räume[key]
    
    @property
    def klassen(self) -> Mapping[str, Klasse]:
        """Im Vertretungsplan beschriebene Klassen.
        
        Alle `Stunde`-, `Kurs`- und `Klausur`-Objekte sind Referenzen. Das heißt,
        Änderungen an diesen Objekten wirken sich auch auf das ursprünglichen
        `Vertretungsplan`-Objekt aus.
        """ 
        klassen: dict[str, Klasse] = {}

        for stunde in self.stunden:
            for klasse in stunde.klassen:
                if klasse not in klassen:
                    klassen[klasse] = Klasse(kürzel=klasse)
                current = klassen[klasse].stunden.get(stunde.periode, tuple())
                new_stunden = dict(klassen[klasse].stunden)
                new_stunden[stunde.periode] = current + (stunde,)
                new_stunden = dict(sorted(new_stunden.items()))
                klassen[klasse].stunden = MappingProxyType(new_stunden)

        for kurs in self.kurse:
            for klasse in kurs.klassen:
                if klasse not in klassen:
                    klassen[klasse] = Klasse(kürzel=klasse)
                new_kurse = dict(klassen[klasse].kurse)
                new_kurse[kurs.kursnummer] = kurs
                new_kurse = dict(sorted(new_kurse.items()))
                klassen[klasse].kurse = MappingProxyType(new_kurse)

        for klausur in self.klausuren:
            klausur_klassen = set()
            for kurs_kürzel in klausur.kurse:
                for kurs in self.kurse:
                    if kurs.kürzel == kurs_kürzel or str(kurs.kursnummer) == kurs_kürzel:
                        klausur_klassen.update(kurs.klassen)
            
            for klasse in klausur_klassen:
                if klasse not in klassen:
                    klassen[klasse] = Klasse(kürzel=klasse)
                if klausur not in klassen[klasse].klausuren:
                    klassen[klasse].klausuren = klassen[klasse].klausuren + (klausur,)

        return MappingProxyType(dict(sorted(((k, v) for k, v in klassen.items() if k), key=lambda x: natural_sort_key(x[0]))))
    
    @property
    def lehrer(self) -> Mapping[str, Lehrer]:
        """Im Vertretungsplan beschriebene Lehrer.
        
        Alle `Stunde`-, `Kurs`- und `Aufsicht`-Objekte sind Referenzen. Das heißt,
        Änderungen an diesen Objekten wirken sich auch auf das ursprünglichen
        `Vertretungsplan`-Objekt aus.
        """
        
        lehrerE: dict[str, Lehrer] = {}
        for stunde in self.stunden:
            for lehrer in stunde.lehrer:
                if lehrer not in lehrerE:
                    lehrerE[lehrer] = Lehrer(kürzel=lehrer)
                current = lehrerE[lehrer].stunden.get(stunde.periode, tuple())
                new_stunden = dict(lehrerE[lehrer].stunden)
                new_stunden[stunde.periode] = current + (stunde,)
                new_stunden = dict(sorted(new_stunden.items()))
                lehrerE[lehrer].stunden = MappingProxyType(new_stunden)

        for kurs in self.kurse:
            lehrer = kurs.lehrer or ""
            if lehrer not in lehrerE:
                lehrerE[lehrer] = Lehrer(kürzel=lehrer)
            new_kurse = dict(lehrerE[lehrer].kurse)
            new_kurse[kurs.kursnummer] = kurs
            new_kurse = dict(sorted(new_kurse.items()))
            lehrerE[lehrer].kurse = MappingProxyType(new_kurse)

        for aufsicht in self.aufsichten:
            for lehrer in aufsicht.lehrer:
                if lehrer not in lehrerE:
                    lehrerE[lehrer] = Lehrer(kürzel=lehrer)
                lehrerE[lehrer].aufsichten = lehrerE[lehrer].aufsichten + (aufsicht,)

        return MappingProxyType(dict(sorted(((k, v) for k, v in lehrerE.items() if k), key=lambda x: natural_sort_key(x[0]))))
    
    @property
    def räume(self) -> Mapping[str, Raum]:
        """Im Vertretungsplan beschriebene Klassen.
        
        Alle `Stunde`-Objekte sind Referenzen. Das heißt, Änderungen an diesen
        Objekten wirken sich auch auf das ursprünglichen `Vertretungsplan`-Objekt aus.
        """
        
        räumeE: dict[str, Raum] = {}
        for stunde in self.stunden:
            for raum in stunde.räume:
                if raum not in räumeE:
                    räumeE[raum] = Raum(kürzel=raum)
                current = räumeE[raum].stunden.get(stunde.periode, tuple())
                new_stunden = dict(räumeE[raum].stunden)
                new_stunden[stunde.periode] = current + (stunde,)
                new_stunden = dict(sorted(new_stunden.items()))
                räumeE[raum].stunden = MappingProxyType(new_stunden)

        return MappingProxyType(dict(sorted(((k, v) for k, v in räumeE.items() if k), key=lambda x: natural_sort_key(x[0]))))
    
    @property
    def abwesendeLehrer(self) -> tuple[str, ...]:
        "Lehrer, die keinen Unterricht haben"
        
        # lehrerMitUnterricht: set[str] = set()
        # lehrerVielleichtKrank: set[str] = set()

        # for klasse in self.klassen.values():
        #     for stunde in [stunde for stunden in klasse.stunden.values() for stunde in stunden]:

        #         if stunde.ausfall and klasse.kurse.get(stunde.kursnummer) is not None:
        #             lehrerVielleichtKrank.add(klasse.kurse.get(stunde.kursnummer).lehrer)

        #         elif stunde.lehreränderung:
        #             if len(stunde.lehrer) > 0:
        #                 lehrerMitUnterricht.update(stunde.lehrer)
        #             if klasse.kurse.get(stunde.kursnummer) is not None:
        #                 lehrerVielleichtKrank.add(klasse.kurse.get(stunde.kursnummer).lehrer)

        #         elif not stunde.ausfall and not stunde.lehreränderung:
        #             if len(stunde.lehrer) > 0:
        #                 lehrerMitUnterricht.update(stunde.lehrer)

        lehrerVielleichtKrank: set[str] = set()

        for kürzel, lehrer in self.lehrer.items():
            lehrerVielleichtKrank.add(kürzel)
            for stunden in lehrer.stunden.values():
                for stunde in stunden:
                    if not stunde.ausfall:
                        lehrerVielleichtKrank.discard(kürzel)

        return tuple(sorted(
            {
                lehrer for lehrer in lehrerVielleichtKrank
                # and lehrer != ""
                # and lehrer is not None
            }, key=natural_sort_key
        ))

    def freieRäume(self, beginn: time = time(0, 0), ende: time = time(23, 59), räume_context: list[str] = []) -> tuple[str, ...]:
        """Gibt die Kürzel der Räume zurück, die zwischen `beginn` und `ende` nicht belegt sind.
        
        Räume, zu denen für den Tag kein Plan existiert sind nicht aufgeführt.
        Um das zu berücksichtigen, sollten in `räume_context` die Kürzel möglicher
        Räume mitgegeben werden, zum Beispiel aus den Plänen der anderen Wochentage.
        """

        frei = set(räume_context)

        for kürzel, raum in self.räume.items():

            frei.add(kürzel)
            for stunden in raum.stunden.values():
                for stunde in stunden:

                    if stunde.beginn is None or stunde.ende is None:
                        continue # keine Aussage möglich -> überspringen
                    if stunde.ausfall is True:
                        continue # Stunde fällt aus
                    if stunde.ende <= beginn or ende <= stunde.beginn:
                        continue # Stunde überschneidet sich nicht mit Zeitraum
                    if kürzel in frei:
                        frei.remove(kürzel)

        return tuple(sorted(list(frei)))

    @classmethod
    def from_xml(cls, data: XML.Element | XML.ElementTree, *, parser: Parser = Parser()) -> Vertretungsplan:
        """Erstellt ein `Vertretungsplan`-Objekt aus einem XML-Dokument.

        Parameters:
            parser (Parser): Parsing-Anweisungen, um die Eigenheiten des Planers zu berücksichtigen
        """
        root = data if isinstance(data, XML.Element) else data.getroot()
        if root is None:
            raise ValueError

        planart = find(root, "Kopf/planart", "text") or None
        
        #======// Datum //=====================//
        datum = None
        if DatumPlan := find(root, "Kopf/DatumPlan", "text"):
            for name, num in {
                "Januar": "01", "Februar": "02", "März": "03", "April": "04",
                "Mai": "05", "Juni": "06", "Juli": "07", "August": "08",
                "September": "09", "Oktober": "10", "November": "11", "Dezember": "12"
            }.items():
                if name in DatumPlan:
                    datumplan = DatumPlan.replace(name, num)
                    break
            try:
                datum = datetime.strptime(datumplan.split(", ")[1], "%d. %m %Y").date()
            except:
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
                        Klausur.from_xml(KlausurTag, parser=parser)
                        for KlausurTag in KlausurenTag.findall("Klausur")
                    ])
        
                # Aufsichten auswerten
                if (AufsichtenTag := KlTag.find("Aufsichten")) is not None:
                    for AufsichtTag in AufsichtenTag.findall("Aufsicht"):
                        aufsicht = Aufsicht.from_xml(AufsichtTag, lehrer=[Kurz])
                                                
                        # Bekannte Aufsichten mergen
                        if (existing_aufsicht := next((a for a in aufsichten if a.beginn == aufsicht.beginn and a.ortinfo == aufsicht.ortinfo), None)):
                            existing_aufsicht.lehrer = tuple(sorted(set(existing_aufsicht.lehrer) | set(aufsicht.lehrer), key=natural_sort_key))
                        else:
                            aufsichten.append(aufsicht)

                # Stunden auswerten
                if (PlTag := KlTag.find("Pl")) is not None:
                    for StdTag in PlTag.findall("Std"):

                        stunde = Stunde.from_xml(StdTag, planart=planart, kontext={Kurz}, parser=parser)

                        # Bekannte Stunden mergen
                        if (existing_stunde := next((s for s in stunden if s.periode == stunde.periode and s.kursnummer == stunde.kursnummer and (s.klassen == stunde.klassen or s.lehrer == stunde.lehrer or s.räume == stunde.räume)), None)):
                            existing_stunde.klassen = tuple(sorted(set(existing_stunde.klassen) | set(stunde.klassen), key=natural_sort_key))
                            existing_stunde.lehrer = tuple(sorted(set(existing_stunde.lehrer) | set(stunde.lehrer), key=natural_sort_key))
                            existing_stunde.räume = tuple(sorted(set(existing_stunde.räume) | set(stunde.räume), key=natural_sort_key))
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
                            existing_kurs.klassen = tuple(sorted(set(existing_kurs.klassen) | set(kurs.klassen), key=natural_sort_key))
                        else:
                            kurse.append(kurs)

        vp = Vertretungsplan(
            datum = datum,
            dateiname = find(root, "Kopf/datei", "text") or None,
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
    
    def to_xml(self, planart: Literal["K", "L", "R"], *, parser: Parser = Parser()) -> XML.ElementTree:
        """Erzeugt ein XML-Dokument für den Vertretungsplan.
        
        Parameters:
            planart (str): Die Planart, die die neuen Quelldaten primär repräsentieren, respektive Klassen, Lehrer oder Räume
            parser (Parser): Formattierungsanweisungen
        """
        import locale
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
        from importlib.metadata import version

        VpMobil = ElementBuilder("VpMobil", attrib={"generator": "vpmobil==" + version("vpmobil")}, children=[
            ElementBuilder("Kopf", children=[
                ElementBuilder("planart", planart),
                ElementBuilder("DatumPlan", self.datum.strftime("%A, %d. %B %Y"))           if self.datum else None,
                ElementBuilder("zeitstempel", self.zeitstempel.strftime("%d.%m.%Y, %H:%M")) if self.zeitstempel else None,
                ElementBuilder("datei", self.dateiname)                                     if self.dateiname else None,
            ]),
            ElementBuilder("FreieTage", children=[
                ElementBuilder("ft", tag.strftime("%y%m%d"))
                for tag in self.freieTage
            ]),
            ElementBuilder("Klassen", children=[
                KlObjekt.to_xml(parser=parser)
                for KlObjekt in (
                    self.klassen.values() if planart == "K" else
                    self.lehrer.values() if planart == "L" else
                    self.räume.values())
            ]),
            ElementBuilder("ZusatzInfo", children=[
                ElementBuilder("ZiZeile", zeile.strip())
                for zeile in (self.zusatzinfo or "").split("\n")
            ])                                                                              if self.zusatzinfo else None
        ])
        return XML.ElementTree(VpMobil)
    
    @classmethod
    def fromfile(cls, pfad: Path | str, *, parser: Parser = Parser()) -> Vertretungsplan:
        """
        Erzeugt ein Vertretungsplan-Objekt aus einer XML-Vertretungsplandatei.

        Raises:
            FileNotFoundError : Wenn die Datei nicht existiert
            ValueError : Wenn die Datei nicht gelesen werden kann
        """
        with open(pfad, encoding="utf-8-sig") as f:
            instance = cls.from_xml(XML.parse(f), parser=parser)
        return instance
    
    def saveasfile(self, pfad: Path | str, overwrite=True, hidden: list[str] = []) -> None:
        """Speichert den ausgewerteten Vertretungsplan als JSON-, YAML- oder TOML-Datei.

        **ACHTUNG**: vpmobil-py hat momentan keine Funktion,
        um so abgespeicherte Dateien wieder einzulesen.

        Parameters:
            pfad (Path | str): Dateipfad der zu erstellenden Datei. Die Dateiendung bestimmt,
                welches Format gewählt wird. Unterstützt werden `.json`, `.yaml` (bzw. `.yml`) und `.toml`.
                Andernfalls wird JSON gewählt.
            overwrite (bool): Ob die Datei überschrieben werden darf, falls sie bereits existiert
            hidden (list[str]): Liste der Felder/Eigenschaften, die nicht in der Datei enthalten
                sein sollen

        Raises:
            FileExistsError: Falls die Datei bereits existiert und `overwrite` `False` ist
        """
        import yaml, json, toml

        data = self.as_dict(hidden=hidden)

        zielpfad = Path(pfad).resolve() # Funktioniert für Path und str
        zielverzeichnis = zielpfad.parent
        zielverzeichnis.mkdir(parents=True, exist_ok=True)

        if zielpfad.exists() and not overwrite:
            raise FileExistsError(f"Datei '{zielpfad}' existiert bereits.")

        if zielpfad.suffix.lower() in ['.yaml', '.yml']:
            with zielpfad.open('w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, indent=4)
        elif zielpfad.suffix.lower() == '.toml':
            def stringify_keys(obj):
                if isinstance(obj, dict):
                    return {str(k): stringify_keys(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [stringify_keys(v) for v in obj]
                return obj
            data = stringify_keys(data)
            with zielpfad.open('w', encoding='utf-8') as f:
                toml.dump(data, f)
        else:
            with zielpfad.open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def save_xml(self, pfad: Path | str, planart: Literal["K", "L", "R"], *, parser: Parser=Parser(), overwrite=True) -> None:
        """Speichert den Vertretungsplan als XML-Datei.

        Parameters:
            pfad (Path | str): Dateipfad der zu erstellenden Datei
            parser (Parser): Formattierungsanweisungen
            overwrite (bool): Ob die Datei überschrieben werden darf, falls sie bereits existiert

        Raises:
            FileExistsError: Falls die Datei bereits existiert und `overwrite` `False` ist
        """

        xmlpretty = prettyxml(self.to_xml(planart=planart, parser=parser))

        zielpfad = Path(pfad).resolve() # Funktioniert für Path und str
        zielverzeichnis = zielpfad.parent
        zielverzeichnis.mkdir(parents=True, exist_ok=True)

        if zielpfad.exists() and not overwrite:
            raise FileExistsError(f"Datei '{zielpfad}' existiert bereits")

        zielpfad.write_text(xmlpretty, encoding="utf-8")
    

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Stunde                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Stunde(VpMobilPyModell):
    """Die Stunden-Klasse enthält alle Informationen einer Unterrichtsstunde, die im
    Vertretungsplan beschrieben wird.

    Um eine Stunde als ausfallend zu kennzeichnen, setze `fach` auf `---`
    """
    periode:         int
    "Unterrichtsperiode der Stunde. Kann `0` sein."
    beginn:          time | None = field(default=None)
    "Beginn der Stunde. Falls keine Uhrzeit angegeben ist, sollte `VertretungsTag.zeitplan` zu Rate gezogen werden."
    ende:            time | None = field(default=None)
    "Ende der Stunde. Falls keine Uhrzeit angegeben ist, sollte `VertretungsTag.zeitplan` zu Rate gezogen werden."
    fach:            str  | None = field(default=None)
    """Fach bzw. Kürzel des Kurses der Stunde. Gibt `None` zurück, wenn die Stunde entfällt.

    Das tatsächlich gängige Kürzel des Fachs kann über
    `klasse.kurse[stunde.kursnummer].fach` erhalten werden.

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
    klassen:         tuple[str, ...] = field(default_factory=tuple)
    "Alle Klassen der Stunde. Gibt `set()` zurück, wenn die Stunde entfällt oder keine Klassen eingetragen sind."
    klassenänderung: bool        = field(default=False)
    "Ob die Klassen der Stunde geändert wurden. Ebenfalls `True`, wenn die Stunde entfällt."
    lehrer:          tuple[str, ...] = field(default_factory=tuple)
    "Alle Lehrer der Stunde. Gibt `set()` zurück, wenn die Stunde entfällt oder keine Lehrer eingetragen sind."
    lehreränderung:  bool        = field(default=False)
    "Ob die Lehrer der Stunde geändert wurden. Ebenfalls `True`, wenn die Stunde entfällt."
    räume:           tuple[str, ...] = field(default_factory=tuple)
    "Alle Räume der Stunde. Gibt `set()` zurück, wenn die Stunde entfällt oder keine Räume eingetragen sind."
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
        return "<" + " ".join(filter(None, [
            ", ".join(self.klassen) if self.klassen else "",
            f"mit {self.fach}" if self.fach else "",
            "bei " + ", ".join(self.lehrer) if self.lehrer else "",
            "in " + ", ".join(self.räume) if self.räume else ""
        ])) + ">"
    
    @property
    def ausfall(self) -> bool:
        """Ob die Stunde entfällt.
        
        Wenn die Stundeninfo das Stichwort `"selbst"` enthält und keine Lehrer
        angegeben sind, wird das ebenfalls als Ausfall interpretiert.
        """
        return self.fach is None or ("selbst" in (self.info or "") and not self.lehrer)
    
    @property
    def änderung(self) -> bool:
        "Ob die Stunde in irgendeiner Weise geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt"
        return self.fachänderung or self.lehreränderung or self.raumänderung or self.klassenänderung
    
    @classmethod
    def from_xml(cls, data: XML.Element, planart: Literal["K", "L", "R"] = "K", *, parser: Parser = Parser(), kontext: tuple[str, ...] = tuple(), kontextgeändert: bool = False) -> Stunde:
        """Erstellt ein `Stunde`-Objekt aus einem XML-Element.

        Parameters:
            planart (str): Typ der Quelldatei, aus dem das Element stammt
            parser (Parser): Parsing-Anweisungen, um die Eigenheiten des Planers zu berücksichtigen
            kontext (set[str]): Klassen, Lehrer, bzw. Räume, die selbst von der Stunde
                betroffen sind. Bei Typ K müssen das Klassen sein, bei Typ R Räume, etc.
                Es sollte mindestens ein Kürzel angegeben sein.
            kontextgeändert (bool): Ob die Klassen, Lehrer, bzw. Räume, die selbst von
                der Stunde betroffen sind, geändert wurden
        """

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
        Le = find(data, "Le", "text")
        Ra = find(data, "Ra", "text")

        fach = find(data, "Fa", "text") or None
        if fach == "---":
            fach = None

        #======// Klassen, Lehrer & Räume //=========//
        nicht_klassen_parser = parser.clone(BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN=False)

        if planart == "K":
            klassen = tuple(sorted(kontext, key=natural_sort_key))
            lehrer = tuple(sorted(nicht_klassen_parser.slice_aufzählung(Le), key=natural_sort_key))
            räume = tuple(sorted(nicht_klassen_parser.slice_aufzählung(Ra), key=natural_sort_key))
            klassenänderung = kontextgeändert
            lehreränderung = "LeAe" in find(data, "Le", "attrib")
            raumänderung = "RaAe" in find(data, "Ra", "attrib")
        elif planart == "L":
            klassen = tuple(sorted(parser.slice_aufzählung(Le), key=natural_sort_key))
            lehrer = tuple(sorted(kontext, key=natural_sort_key))
            räume = tuple(sorted(nicht_klassen_parser.slice_aufzählung(Le), key=natural_sort_key))
            klassenänderung = "LeAe" in find(data, "Le", "attrib")
            lehreränderung = kontextgeändert
            raumänderung = "RaAe" in find(data, "Ra", "attrib")
        elif planart == "R":
            klassen = tuple(sorted(parser.slice_aufzählung(Le), key=natural_sort_key))
            lehrer = tuple(sorted(nicht_klassen_parser.slice_aufzählung(Le), key=natural_sort_key))
            räume = tuple(sorted(kontext, key=natural_sort_key))
            klassenänderung = "RaAe" in find(data, "Ra", "attrib")
            lehreränderung = "LeAe" in find(data, "Le", "attrib")
            raumänderung = kontextgeändert

        return Stunde(
            periode = int(data.find("St").text),
            beginn = beginn,
            ende = ende,
            fach = fach,
            fachmeta = find(data, "Ku2", "text") or None,
            fachänderung = "FaAe" in find(data, "Fa", "attrib"),
            klassen = klassen,
            klassenänderung = klassenänderung,
            lehrer = lehrer,
            lehreränderung = lehreränderung,
            räume = räume,
            raumänderung = raumänderung,
            kursnummer = kursnummer,
            info = find(data, "If", "text") or None
        )
        
    def to_xml(self, planart: Literal["K", "L", "R"], *, parser: Parser = Parser()) -> XML.Element:
        """Erzeugt ein XML-Element für die Stunde.
        
        Parameters:
            planart (str): Die Planart, die die neuen Quelldaten primär repräsentieren, respektive Klassen, Lehrer oder Räume
            parser (Parser): Formattierungsanweisungen
        """
        Std = ElementBuilder("Std", children=[
            ElementBuilder("St", self.periode),
            ElementBuilder("Beginn", self.beginn.strftime("%H:%M"))         if self.beginn else None,
            ElementBuilder("Ende", self.ende.strftime("%H:%M"))             if self.ende else None,
            ElementBuilder("Fa", self.fach or "" if not self.ausfall else "---"),
            ElementBuilder("Ku2", self.fachmeta)                            if self.fachmeta else None,
            ElementBuilder("Le",
                parser.AUFZÄHLUNGS_TRENNZEICHEN.join(self.lehrer if planart != "L" else self.klassen),
                {"LeAe": "LeGeaendert"} if (self.lehreränderung if planart != "L" else self.klassenänderung) else {}
            ),
            ElementBuilder("Ra",
                parser.AUFZÄHLUNGS_TRENNZEICHEN.join(self.räume if planart != "R" else self.klassen),
                {"RaAe": "RaGeaendert"} if (self.raumänderung if planart != "R" else self.klassenänderung) else {}
            ),
            ElementBuilder("Nr", self.kursnummer),
            ElementBuilder("If", self.info),
        ])
        return Std


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Kurs                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Kurs(VpMobilPyModell):
    """Die Kurs-Klasse enthält alle Informationen zu einem im Vertretungsplan
    beschriebenen Kurs. In der Regel sind alle Kurse vorhanden, auch die,
    die am betreffenden Tag keine Stunde haben.
    """
    kursnummer: int | None
    "Kursnummer des Kurses"
    kürzel:     str | None = field(default=None)
    "Gruppenbezeichnung des Kurses. Falls in den Quelldaten nicht vorhanden, wird stattdessen das Fach zurückgegeben."
    fach:       str | None = field(default=None)
    "Fach des Kurses"
    lehrer:     str | None = field(default=None)
    "Lehrer des Kurses"
    klassen:         tuple[str, ...] = field(default_factory=tuple)
    "Klassen, die Anteile am Kurs haben"

    def __repr__(self) -> str:
        return "<" + " ".join(filter(None, [
            "Kurs",
            f"{self.kürzel}" if self.kürzel else "",
            f"bei {self.lehrer}" if self.lehrer else "",
            f"(Kursnummer {self.kursnummer})" if self.kursnummer else ""
        ])) + ">"

    @classmethod
    def from_xml(cls, data: XML.Element, klassen: tuple[str, ...]) -> Kurs:
        """Erstellt ein `Kurs`-Objekt aus einem XML-Element.

        Parameters:
            klassen (set[str]): Klassen, die den Kurs besuchen.
                Da in den Quelldaten die Klasse des Kurses nur implizit über die
                XML-Hierarchie gegeben ist, muss sie und etwaige andere bei Bedarf
                manuell als Argument mitgegeben werden.       
        """
        return Kurs(
            kursnummer = int(find(data, "UeNr", "text")) if find(data, "UeNr", "text") else None,
            kürzel = find(data, "UeNr", "attrib").get("UeGr", None) or find(data, "UeNr", "attrib").get("UeFa", None),
            fach = find(data, "UeNr", "attrib").get("UeFa", None),
            lehrer = find(data, "UeNr", "attrib").get("UeLe", None),
            klassen = klassen
        )

    def to_xml(self, *, parser: Parser = Parser()) -> XML.Element:
        """Erzeugt ein XML-Element für den Kurs.
        """
        return ElementBuilder("Ue", children=[
            ElementBuilder("UeNr", self.kursnummer, {
                **({"UeLe": self.lehrer} if self.lehrer else {}),
                **({"UeGr": self.kürzel} if self.kürzel else {}),
                **({"UeFa": self.fach} if self.fach else {}),
            })
        ])


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                        Aufsicht                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Aufsicht(VpMobilPyModell):
    """Die Aufsicht-Klasse enthält alle Informationen zu einer im Vertretungsplan
    beschriebenen Lehreraufsicht.
    """
    lehrer:          tuple[str, ...] = field(default_factory=tuple)
    "Lehrer, für die die Aufsicht angesetzt ist"
    vorStunde: int  | None = field(default=None)
    "Unterrichtsperiode, in deren davoriger Pause die Aufsicht stattfindet"
    beginn:    time | None = field(default=None)
    "Uhrzeit der Aufsicht"
    zeitinfo:  str  | None = field(default=None)
    "Hinweis zum Zeitpunkt der Aufsicht"
    ortinfo:   str  | None = field(default=None)
    "Hinweis zum Ort der Aufsicht"

    def __repr__(self):
        return "<" + " ".join(filter(None, [
            "Aufsicht",
            "durch " + ", ".join(self.lehrer) if self.lehrer else "",
            f"ab {self.beginn.strftime("%H:%M")}" if self.beginn else ""
        ])) + (((", " if self.lehrer or self.beginn else "") + (self.ortinfo)) if self.ortinfo else "") + ">"

    @classmethod
    def from_xml(cls, data: XML.Element, lehrer: tuple[str, ...]) -> Aufsicht:
        """Erstellt ein `Aufsicht`-Objekt aus einem XML-Element.

        Parameters:
            lehrer (set[str]): Lehrer, die von der Aufsicht betroffen sind
        """

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

    def to_xml(self, *, parser: Parser = Parser()) -> XML.Element:
        """Erzeugt ein XML-Element für die Aufsicht.
        """
        return ElementBuilder("Aufsicht", children=[
            ElementBuilder("AuVorStunde", str(self.vorStunde))          if self.vorStunde else None,
            ElementBuilder("AuUhrzeit", self.beginn.strftime("HH:MM"))  if self.beginn else None,
            ElementBuilder("AuZeit", self.zeitinfo)                     if self.zeitinfo else None,
            ElementBuilder("AuOrt", self.ortinfo)                       if self.ortinfo else None
        ])


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Klausur                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class Klausur(VpMobilPyModell):
    """Die Klausur-Klasse enthält die Informationen zu einer im Vertretungsplan
    beschriebenen Klausur.
    """
    kurse:   tuple[str, ...]         = field(default_factory=tuple)
    "Kurse, für die die Klausur angesetzt ist"
    lehrer:  str       | None = field(default=None)
    "Lehrer, die die Klausur beaufsichtigen"
    periode: int       | None = field(default=None)
    "Unterrichtsperiode, in der die Klausur beginnt. Kann `0` sein."
    beginn:  time      | None = field(default=None)
    "Uhrzeit, zu der die Klausur beginnt"
    dauer:   timedelta | None = field(default=None)
    "Dauer der Klausur"
    info:    str       | None = field(default=None)
    "Zusätzliche Informationen zur Klausur"

    def __repr__(self):
        return "<" + " ".join(filter(None, [
            "Klausur",
            "für " + ", ".join(self.kurse) if self.kurse else "",
            f"ab {self.beginn.strftime("%H:%M")}" if self.beginn else "",
        ])) + ">"

    @classmethod
    def from_xml(cls, data: XML.Element, *, parser: Parser = Parser()) -> Klausur:
        """Erstellt ein `Klausur`-Objekt aus einem XML-Element.

        Parameters:
            parser (Parser): Parsing-Anweisungen, um die Eigenheiten des Planers zu berücksichtigen
        """

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
            kurse=parser.slice_aufzählung(find(data, "KlKurs", "text")) or None,
            lehrer=find(data, "KlKursleiter", "text") or None,
            periode=periode,
            beginn=beginn,
            dauer=dauer,
            info=find(data, "KlKinfo", "text") or None
        )
    
    def to_xml(self, *, parser: Parser = Parser()) -> XML.Element:
        """Erzeugt ein XML-Element für die Klausur.
        
        Parameters:
            parser (Parser): Formattierungsanweisungen
        """
        return ElementBuilder("Klausur", children=[
            ElementBuilder("KlKurs", parser.AUFZÄHLUNGS_TRENNZEICHEN.join(self.kurse)) if self.kurse else None,
            ElementBuilder("KlKursleiter", self.lehrer)                                if self.lehrer else None,
            ElementBuilder("KlStunde", str(self.periode))                              if self.periode or self.periode == 0 else None,
            ElementBuilder("KlBeginn", self.beginn.strftime("HH:MM"))                  if self.beginn else None,
            ElementBuilder("KlDauer", str(int(self.dauer.total_seconds()/60)))         if self.dauer else None,
            ElementBuilder("Klinfo", self.info)                                        if self.info else None,
        ])


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                      KLR-Ansichten                                       │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(frozen=False)
class KLRProxyBase(VpMobilPyModell):
    kürzel:  str # notwendig, um default follows non-default nicht zu verletzen
    stunden: Mapping[int, Collection[Stunde]] = field(default_factory=lambda: MappingProxyType({}))
    "Unterrichtsstunden gruppiert nach Unterrichtsperiode"
    
    def __getitem__(self, key) -> tuple[Stunde]:
        return self.stunden.get(key, None)


@dataclass(frozen=False)
class Klasse(KLRProxyBase):
    "Proxy für auf eine bestimmte Klasse bezogene Informationen im Vertretungsplan"
    kürzel:  str
    "Bezeichner der Klasse"
    kurse: Mapping[int, Kurs] = field(default_factory=lambda: MappingProxyType({}))
    "Kurse, an denen die Klasse Anteile hat"
    klausuren: Collection[Klausur] = field(default_factory=tuple)
    "Klausuren der Klasse"

    def __repr__(self):
        return f"<Klasse '{self.kürzel}'>"
    
    def to_xml(self, *, parser: Parser = Parser()) -> XML.Element:
        """Erzeugt ein XML-Element für die Klasse.
        
        Parameters:
            parser (Parser): Formattierungsanweisungen
        """
        Kl = ElementBuilder("Kl", children=[
            ElementBuilder("Kurz", self.kürzel),
            ElementBuilder("Pl", children=[
                StdObjekt.to_xml(planart="K", parser=parser)
                for stunden in self.stunden.values() for StdObjekt in stunden
            ]),
            ElementBuilder("Unterricht", children=[
                UeObjekt.to_xml()
                for UeObjekt in self.kurse.values()
            ]),
            ElementBuilder("Klausuren", children=[
                KlausurObjekt.to_xml()
                for KlausurObjekt in self.klausuren
            ])
        ])
        return Kl

@dataclass(frozen=False)
class Lehrer(KLRProxyBase):
    "Proxy für auf einen bestimmten Lehrer bezogene Informationen im Vertretungsplan"
    kürzel:  str
    "Bezeichner des Lehrers"
    kurse: Mapping[int, Kurs]   = field(default_factory=lambda: MappingProxyType({}))
    "Kurse des Lehrers, zugänglich über die Kursnummer"
    aufsichten: Collection[Aufsicht] = field(default_factory=tuple)
    "Aufsichten des Lehrers"

    def __repr__(self):
        return f"<Lehrer '{self.kürzel}'>"
    
    def to_xml(self, *, parser: Parser = Parser()) -> XML.Element:
        """Erzeugt ein XML-Element für den Lehrer.
        
        Parameters:
            parser (Parser): Formattierungsanweisungen
        """
        Kl = ElementBuilder("Kl", children=[
            ElementBuilder("Kurz", self.kürzel),
            ElementBuilder("Pl", children=[
                StdObjekt.to_xml(planart="L", parser=parser)
                for stunden in self.stunden.values() for StdObjekt in stunden
            ]),
            ElementBuilder("Unterricht", children=[
                UeObjekt.to_xml()
                for UeObjekt in self.kurse.values()
            ]),
            ElementBuilder("Aufsichten", children=[
                AufsichtObjekt.to_xml()
                for AufsichtObjekt in self.aufsichten
            ])
        ])
        return Kl

@dataclass(frozen=False)
class Raum(KLRProxyBase):
    "Proxy für auf einen bestimmten Raum bezogene Informationen im Vertretungsplan"
    kürzel:  str
    "Bezeichner des Raumes"
    
    def __repr__(self):
        return f"<Raum '{self.kürzel}'>"
    
    def to_xml(self, *, parser: Parser = Parser()) -> XML.Element:
        """Erzeugt ein XML-Element für den Raum.
        
        Parameters:
            parser (Parser): Formattierungsanweisungen
        """
        Kl = ElementBuilder("Kl", children=[
            ElementBuilder("Kurz", self.kürzel),
            ElementBuilder("Pl", children=[
                StdObjekt.to_xml(planart="R", parser=parser)
                for stunden in self.stunden.values() for StdObjekt in stunden
            ])
        ])
        return Kl