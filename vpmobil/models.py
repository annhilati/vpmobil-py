from __future__ import annotations
from dataclasses import dataclass, field, InitVar
from xml.etree import ElementTree as XML
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Literal, Any
import re

from vpmobil.utils import prettyxml, slice_aufzählung, add_Element
from vpmobil import config

@dataclass(init=True, eq=False)
class VpMobilPyModell:

    data:    XML.Element            = field(init=True)
    _planart: Literal["K", "L", "R"] = field(init=True)

    def _tag_data(self, tag: str, attr: Literal["text", "attrib"]) -> str | dict:
        "Gibt ein Attribut eines Untertags zurück. Ist niemals `None`. Stattdessen wird `\"\"` oder `{}` zurückgegeben."
        
        # Hier mal hinzufügen, dass direkt Keys aus Element.attrib angefordert werden können?
        element = self.data.find(tag)
        match attr:
            case "text":    return getattr(element, attr, "")
            case "attrib":  return getattr(element, attr, {})
            case _:         raise ValueError

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
            VpMobilPyModell: lambda m: m.as_dict()
        }

        def apply_converter(value: Any) -> Any:
            if isinstance(value, list):
                return [apply_converter(v) for v in value]
            if isinstance(value, tuple):
                return list(apply_converter(v) for v in value)
            if isinstance(value, dict):
                return {k: apply_converter(v) for k, v in value.items()}

            for t, conv in converters.items():
                if isinstance(value, t):
                    return conv(value)

            return value

        result = {}
        for name in dir(self.__class__):
            if isinstance(getattr(self.__class__, name, None), property) and not name.startswith("_"):
                val = getattr(self, name)
                result[name] = apply_converter(val)

        try: import json; _ = json.dumps(result, ensure_ascii=False)
        except: raise AssertionError(config.ERRORS.KEY_VALUE_ASSERTION)

        return result


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                      VertretungsTag                                      │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(eq=False)
class VertretungsTag(VpMobilPyModell):
    """VertretungsTag ist die Basisklasse für Vertretungspläne.

    Beim Versuch einer Instanzierung wird entsprechend dem Inhalt automatisch
    eine Instanz von `VertretungsTag`, `LehrerVertretungsTag` oder
    `RaumVertretungsTag` zurückgegeben.
    """

    data: XML.ElementTree                     = field(init=True)
    _planart: InitVar[Literal["K", "L", "R"]] = field(init=False, default=None) # what a nice workaround

    @property
    def _planart(self) -> Literal["K", "L", "R"]:
        return self._tag_data("Kopf/planart", "text")

    def __new__(cls, _data: XML.ElementTree):
        if cls is VertretungsTag:
            if _data.find("Kopf/planart") is None or _data.find("Kopf/planart").text is None:
                raise ValueError(config.ERRORS.UNKNWON_XML)
            
            match _data.find("Kopf/planart").text:
                case "K":
                    return KlassenVertretungsTag(_data)
                case "L":
                    return LehrerVertretungsTag(_data)
                case "R":
                    return RaumVertretungsTag(_data)
                case _:
                    raise ValueError(f"Planart muss eins von 'K', 'L' oder 'R' sein, nicht '{_data.find('Kopf/planart').text}'")
                
        return super().__new__(cls)
                        
    def __repr__(self):
        return f"<Vertretungsplan (Typ {self._planart}) vom {self.datum.strftime(r'%d.%m.%Y')}>"
        
    @property
    def zeitstempel(self) -> datetime | None:
        "Veröffentlichungszeitpunkt des Vertretungsplans bzw. der letzten Änderung"
        if s := self._tag_data("Kopf/zeitstempel", "text"):
            return datetime.strptime(s, r"%d.%m.%Y, %H:%M")
        return None
        
    @property
    def datei(self) -> str | None:
        "Originaler Dateiname der Quelldatei"
        return self._tag_data("Kopf/datei", "text") or None

    @property
    def datum(self) -> date | None:
        "Datum für das der Vertretungsplan gilt"
        import locale
        
        if DatumPlan := self._tag_data("Kopf/DatumPlan", "text"):
            for s in ["de_DE.UTF-8", "German_Germany"]:
                try:
                    locale.setlocale(locale.LC_TIME, s)
                    return datetime.strptime(DatumPlan, (r"%A, %d. %B %Y")).date()
                except: continue
            raise ValueError(f"Das Datum {DatumPlan} konnte nicht dekodiert werden. Bitte erstelle ein Issue im Bugtracker von vpmobil-py auf GitHub (https://github.com/annhilati/vpmobil-py/issues)")
        return None
    
    @property
    def freieTage(self) -> list[date]:
        "Unterrichtsfreie Tage"
        if freieTage := self.data.find("FreieTage"):
            return [
                datetime.strptime(ft.text, "%y%m%d").date()
                for ft in freieTage.findall("ft")
                if ft.text is not None
            ]
        return []
    
    @property
    def zusatzInfo(self) -> str | None:
        """Zusätzliche Informationen zum Tag. Kann mehrzeilig sein.
        """
        if zusatzInfo := self.data.find('ZusatzInfo'):
            return '\n'.join([
                ziZeile.text
                for ziZeile in zusatzInfo.findall('ZiZeile')
                if ziZeile.text
            ])
        return None

    @property
    def zeitplan(self) -> dict[int, tuple[time | None, time | None]]:
        """Gibt die Unterrichtsperioden mit Beginn- und Endzeiten zurück. Die Schlüssel
        sind die Periodennummern, die Werte sind Tupel aus Beginn- und Endzeit.
        """
        result = {}
        if self._planart == "K":
            klasselikes: list[Klasse] = self.klassen.values()
        elif self._planart == "L":
            klasselikes: list[Lehrer] = self.lehrer.values()
        elif self._planart == "R":
            klasselikes: list[Raum] = self.räume.values()
        else:
            raise NotImplementedError
        for klasse in klasselikes:
            for stunden in klasse.stunden.values():
                for stunde in stunden:
                    if stunde.periode in result:
                        beginn, ende = result[stunde.periode]
                        if beginn is None and stunde.beginn is not None:
                            beginn = stunde.beginn
                        if ende is None and stunde.ende is not None:
                            ende = stunde.ende
                        result[stunde.periode] = (beginn, ende)
                        continue
                    result[stunde.periode] = (stunde.beginn, stunde.ende)

            if (KlStunden := klasse.data.find("KlStunden")):
                for KlSt in KlStunden.findall("KlSt"):
                    if not KlSt.text or KlSt.text in result or not KlSt.attrib.get("ZeitVon") or not KlSt.attrib.get("ZeitBis"):
                        continue
                    result[int(KlSt.text)] = (
                        datetime.strptime(KlSt.attrib.get("ZeitVon"), "%H:%M").time(),
                        datetime.strptime(KlSt.attrib.get("ZeitBis"), "%H:%M").time()
                    )

        return {k: result[k] for k in sorted(result.keys())}
    
    def freieRäume(self, beginn: time = time(0, 0), ende: time = time(23, 59), räume_context: list[str] = []) -> list[str]:
        """Gibt die Kürzel der Räume zurück, die zwischen `beginn` und `ende` nicht belegt sind.
        
        Räume, zu denen für den Tag kein Plan existiert sind nicht aufgeführt.
        Um das zu berücksichtigen, sollten in `räume_context` die Kürzel möglicher
        Räume mitgegeben werden, zum Beispiel aus den Plänen der anderen Wochentage.
        """

        from vpmobil.extensions import reparser
        
        data = reparser.RaumPerspektive(self)

        frei = set(räume_context)

        for kürzel, raum in data.räume.items():

            frei.add(kürzel)
            for periode, stunden in raum.stunden.items():
                for stunde in stunden:

                    if stunde.beginn is None or stunde.ende is None:
                        continue # keine Aussage möglich -> überspringen
                    if stunde.ausfall is True:
                        continue # Stunde fällt aus
                    if stunde.ende <= beginn or ende <= stunde.beginn:
                        continue # Stunde überschneidet sich nicht mit Zeitraum
                    if kürzel in frei:
                        frei.remove(kürzel)

        return sorted(list(frei))
            
    @classmethod
    def fromfile(cls, pfad: Path | str, /) -> KlassenVertretungsTag | LehrerVertretungsTag | RaumVertretungsTag:
        """
        Erzeugt ein Vertretungsplan-Objekt aus einer XML-Vertretungsplandatei.

        Raises:
            FileNotFoundError : Wenn die Datei nicht existiert
            ValueError : Wenn die Datei nicht gelesen werden kann
        """
        with open(pfad, encoding="utf-8-sig") as f:
            instance = cls(XML.parse(f))
        return instance
    
    def save_source(self, pfad: Path | str = "./datei.xml", overwrite=True) -> None:
        """Speichert den Vertretungsplan als XML-Datei.

        Parameters:
            pfad (Path | str): Dateipfad der zu erstellenden Datei
            overwrite (bool): Ob die Datei überschrieben werden darf, falls sie bereits existiert

        Raises:
            FileExistsError: Falls die Datei bereits existiert und `overwrite` `False` ist
        """

        xmlpretty = prettyxml(self.data)

        zielpfad = Path(pfad).resolve() # Funktioniert für Path und str
        zielverzeichnis = zielpfad.parent
        zielverzeichnis.mkdir(parents=True, exist_ok=True)

        if zielpfad.exists() and not overwrite:
            raise FileExistsError(f"Datei '{zielpfad}' existiert bereits.")

        zielpfad.write_text(xmlpretty, encoding="utf-8")

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

    def _Kl_Elemente(self) -> list[XML.Element]:
        if klassen := self.data.find('.//Klassen'):
            return [
                kl for kl in klassen.findall(".//Kl")
                if kl.find('Kurz') is not None
            ]
        return []


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                  KlassenVertretungsTag                                   │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class KlassenVertretungsTag(VertretungsTag):
    """Klasse für Vertretungspläne aus Perspektive der Klassen.
    
    Einzelne Klassen sind neben `~.klassen` über `__getitem__` und Subskription verfügbar: 
    ```
    data: KlassenVertretungsTag = vp.fetch()
    klasse = data["10a"]
    ```
    """

    def __getitem__(self, v) -> Klasse | None:
        return self.klassen.get(v)

    @property
    def lehrerKrank(self) -> list[str]:
        "Kürzel der Lehrer, die unplanmäßig keinen Unterricht haben"
        
        lehrerMitUnterricht: set[str] = set()
        lehrerVielleichtKrank: set[str] = set()

        for klasse in self.klassen.values():
            for stunde in [stunde for stunden in klasse.stunden.values() for stunde in stunden]:

                if stunde.ausfall and klasse.kurse.get(stunde.kursnummer) is not None:
                    lehrerVielleichtKrank.add(klasse.kurse.get(stunde.kursnummer).lehrer)

                elif stunde.lehrergeändert:
                    if len(stunde.lehrer) > 0:
                        lehrerMitUnterricht.update(stunde.lehrer)
                    if klasse.kurse.get(stunde.kursnummer) is not None:
                        lehrerVielleichtKrank.add(klasse.kurse.get(stunde.kursnummer).lehrer)

                elif not stunde.ausfall and not stunde.lehrergeändert:
                    if len(stunde.lehrer) > 0:
                        lehrerMitUnterricht.update(stunde.lehrer)

        return sorted(
            {
                lehrer for lehrer in lehrerVielleichtKrank
                if lehrer not in lehrerMitUnterricht
                and lehrer != ""
                and lehrer is not None
            }
        )

    
    @property
    def klassen(self) -> dict[str, Klasse]:
        "Im Vertretungsplan beschriebene Klassen"
        return {
            Klasse(element, self._planart).kürzel: Klasse(element, self._planart)
            for element in self._Kl_Elemente()
        }


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                   LehrerVertretungsTag                                   │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class LehrerVertretungsTag(VertretungsTag):
    """Klasse für Vertretungspläne aus Perspektive der Lehrer.
    
    Einzelne Lehrer sind neben `~.lehrer` über `__getitem__` und Subskription verfügbar: 
    ```
    data: LehrerVertretungsTag = vp.fetch()
    lehrer = data["Ah"]
    ```
    """

    def __getitem__(self, v) -> Lehrer | None:
        return self.lehrer.get(v)

    @property
    def lehrer(self) -> dict[str, Lehrer]:
        "Im Vertretungsplan beschriebene Lehrer"
        return {
            Lehrer(element, self._planart).kürzel: Lehrer(element, self._planart)
            for element in self._Kl_Elemente()
        }    
    

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    RaumVertretungsTag                                    │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class RaumVertretungsTag(VertretungsTag):
    """Klasse für Vertretungspläne aus Perspektive der Räume.
    
    Einzelne Räume sind neben `~.räume` über `__getitem__` und Subskription verfügbar: 
    ```
    data: RaumVertretungsTag = vp.fetch()
    raum = data["E07"]
    ```
    """

    def __getitem__(self, v) -> Raum | None:
        return self.räume.get(v)
    
    @property
    def räume(self) -> dict[str, Raum]:
        "Im Vertretungsplan beschriebene Räume"
        return {
            Raum(element, self._planart).kürzel: Raum(element, self._planart)
            for element in self._Kl_Elemente()
        }   


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                      KlasseLikeBase                                      │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class KlasseLikeBase(VpMobilPyModell):
    
    def __getitem__(self, v) -> list[Stunde]:
        return self.stunden.get(v) or []
    
    @property
    def kürzel(self) -> str:
        return self.data.find('Kurz').text
    
    @property
    def stunden(self) -> dict[int, list[Stunde]]:
        """Alle Unterrichtsstunden als Dictionary. Die Schlüssel sind die
        Unterrichtsperioden, die Werte sind Listen von `Stunden`-Objekten.
        """

        fin: dict[int, list[Stunde]] = {}
        pl = self.data.find("Pl")
        for std in pl.findall("Std"):
            stunde = Stunde(std, self._planart, self.kürzel)
            nr = stunde.periode
            if nr is not None:
                if fin.get(stunde.periode) is None:
                    fin[stunde.periode] = [stunde]
                else:
                    fin[stunde.periode].append(stunde)
        return fin    

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                           Klasse                                         │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Klasse(KlasseLikeBase):
    """Klasse für den Vertretungsplan einer bestimmten Klasse.
    
    Die Stunden einer Periode sind neben `~.stunden` über `__getitem__` und Subskription verfügbar: 
    ```
    data: Klasse = tag.klassen["10a"]
    stunden_zur_dritten = data[3]
    ```
    """

    def __repr__(self):
        return f"<Klasse '{self.kürzel}'>"
    
    @property
    def kurse(self) -> dict[int, Kurs]:
        "Kurse der Klasse als Dictionary. Die Keys sind die Kursnummern der Kurse." 
        if unterricht := self.data.find("Unterricht"):
            return {
                Kurs(ue, self._planart).kursnummer: Kurs(ue, self._planart)
                for ue in unterricht.findall("Ue")
            }
        return {}
    
    @property
    def klausuren(self) -> list[Klausur]:
        "Klausuren der Klasse"
        if klausuren := self.data.find("Klausuren"):
            return [
                Klausur(klausur, self._planart)
                for klausur in klausuren.findall("Klausur")
            ]
        return []
    

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                           Lehrer                                         │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯
    
class Lehrer(KlasseLikeBase):
    """Klasse für den Vertretungsplan eines bestimmten Lehrers.
    
    Die Stunden einer Periode sind neben `~.stunden` über `__getitem__` und Subskription verfügbar: 
    ```
    data: Lehrer = tag.lehrer["Ah"]
    stunden_zur_dritten = data[3]
    ```
    """

    def __repr__(self):
        return f"<Lehrer '{self.kürzel}'>"
    
    @property
    def aufsichten(self) -> list[Aufsicht]:
        """Aufsichten des Lehrers"""
        if aufsichten := self.data.find("Aufsichten"):
            return [
                Aufsicht(aufsicht, self._planart)
                for aufsicht in aufsichten.findall("Aufsicht")
            ]
        return []


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                           Raum                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Raum(KlasseLikeBase):
    """Klasse für den Vertretungsplan eines bestimmten Raums.
    
    Die Stunden einer Periode sind neben `~.stunden` über `__getitem__` und Subskription verfügbar: 
    ```
    data: Raum = tag.räume["E07"]
    stunden_zur_dritten = data[3]
    ```
    """

    def __repr__(self):
        return f"<Raum '{self.kürzel}'>"


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Aufsicht                                         │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Aufsicht(VpMobilPyModell):
    """Klasse, die eine Lehreraufsicht repräsentiert.
    """

    def __repr__(self):
        return f"<Aufsicht ab '{self.zeit}' in '{self.ort}'>"

    @property
    def vorStunde(self) -> int | None:
        "Unterrichtsperiode, vor der die Aufsicht stattfindet"
        return self._tag_data("AuVorStunde", "text") or None
    
    @property
    def uhrzeit(self) -> time | None:
        "Uhrzeit der Aufsicht"
        if s := self._tag_data("AuUhrzeit", "text"):
            return datetime.strptime(s, "%H:%M").time()  
        return None
    
    @property
    def zeit(self) -> str | None:
        "Hinweis zum Zeitpunkt der Aufsicht"
        return self._tag_data("AuZeit", "text") or None
    
    @property
    def ort(self) -> str | None:
        "Hinweis zum Ort der Aufsicht"
        return self._tag_data("AuOrt", "text") or None


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Klausur                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Klausur(VpMobilPyModell):
    """Klasse, die eine Klausur repräsentiert.
    """

    def __repr__(self):
        return f"<Klausur für '{self.kurs}' ab '{self.beginn}'>"

    @property
    def kurs(self) -> str | None:
        "Kurs für den die Klausur ansteht"
        return self._tag_data("KlKurs", "text") or None

    @property
    def lehrer(self) -> str | None:
        "Lehrer des Kurses für den die Klausur ansteht"
        return self._tag_data("KlKursleiter", "text") or None
    
    @property
    def periode(self) -> int | None:
        "Unterrichtsperiode, zu der die Klausur beginnt. Kann `0` sein."
        if s := self._tag_data("KlStunde", "text"):
            return int(s)
        return None
    
    @property
    def beginn(self) -> time | None:
        "Beginn der Klausur"
        if s := self._tag_data("KlBeginn", "text"):
            return datetime.strptime(s, "%H:%M").time()
        return None
    
    @property
    def dauer(self) -> timedelta | None:
        "Dauer der Klausur"
        if s := self._tag_data("KlDauer", "text"):
            return timedelta(minutes=int(s))
        return None
    
    @property
    def info(self) -> str | None:
        "Zusätzliche Informationen zur Klausur"
        return self._tag_data("KlKinfo", "text") or None
    

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Stunde                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(eq=False)
class Stunde(VpMobilPyModell):
    """Klasse, die eine bestimmte Unterrichtsstunde repräsentiert.
    """

    _context: str = field(init=True) # Kürzel der Klasse/des Lehrers/des Raums, zu der/dem die Stunde gehört
    
    def __repr__(self):
        if self.ausfall:
            return f"<Ausfall: '{self.info}'>"
        return f"<\'{', '.join(self.klassen)}\' mit \'{self.fach}\' bei \'{', '.join(self.lehrer)}\' in \'{', '.join(self.räume)}\'>"
    
    @property
    def periode(self) -> int:
        "Unterrichtsperiode der Stunde. Kann `0` sein."
        return int(self.data.find("St").text)

    @property
    def beginn(self) -> time | None:
        "Beginn der Stunde. Falls keine Uhrzeit angegeben ist, sollte `VertretungsTag.zeitplan` zu Rate gezogen werden."
        if s := self._tag_data("Beginn", "text"):
            return datetime.strptime(s, "%H:%M").time()  
        return None
    
    @property
    def ende(self) -> time | None:
        "Ende der Stunde. Falls keine Uhrzeit angegeben ist, sollte `VertretungsTag.zeitplan` zu Rate gezogen werden."
        if s := self._tag_data("Ende", "text"):
            return datetime.strptime(s, "%H:%M").time() 
        return None
    
    @property
    def ausfall(self) -> bool:
        """Ob die Stunde entfällt.
        
        Wenn die Stundeninfo das Stichwort `"selbst"` enthält und weder Lehrer
        noch Räume angegeben sind, wird das ebenfalls als Ausfall interpretiert.
        """
        return self._tag_data("Fa", "text") == "---" or ("selbst" in (self.info or "") and not self.räume + self.lehrer)

    @property
    def fach(self) -> str | None:
        """Fach bzw. Kursbezeichnung der Stunde. Gibt `None` zurück, wenn die Stunde entfällt.

        Das tatsächlich das gängige Kürzel des Fachs kann über
        `klasse.kurs(stunde.kursnummer).fach` erhalten werden.

        Bei Unsicherheit mit Fallback wäre beispielsweise denkbar:
        ```
        stunde.fach if klasse.kurse[stunde.kursnummer] is None else klasse.kurse[stunde.kursnummer].fach
        ```
        """
        if self.ausfall:
            return None
        if (s := self._tag_data("Fa", "text")):
            return s
        return None
    
    @property
    def fachmeta(self) -> str | None:
        """Metainformation über das Fach das normalerweise in dieser Stunde stattfindet.

        Das Verhalten dieses Werts ist etwas unintuitiv. Er wird hauptsächlich bei
        Stunden von Kursen gesetzt, die mehrere inhatlich parallele Gruppen haben,
        beispielsweise bei Sport (wenn es separate Kurse für Jungen und Mädchen gibt),
        Profilen, Religionsgruppen und Kursen der Oberstufe generell.
        
        Dieser Wert ist bei entsprechenden Stunden immer gesetzt, auch wenn die Stunde
        entfällt oder das Fach geändert wurde.
        """
        if (s := self._tag_data("Ku2", "text")):
            return s
        return None

    @property
    def klassen(self) -> list[str]:
        """Alle Klassen der Stunde. Gibt `[]` zurück, wenn die Stunde entfällt oder
        keine Klassen eingetragen sind. Falls die Stunden einer Klasse ausgewertet
        werden, wird hier höchstens nur diese Klasse zurückgegeben.
        """
        if self._planart == "K":
            return [self._context] if not self.ausfall else []
        elif self._planart == "L":
            return slice_aufzählung(self.data.find("Le").text) if self._tag_data("Le", "text") else []
        elif self._planart == "R":
            return slice_aufzählung(self.data.find("Ra").text) if self._tag_data("Ra", "text") else []

    @property
    def lehrer(self) -> list[str]:
        """Alle Lehrer der Stunde. Gibt `[]` zurück, wenn die Stunde entfällt oder
        keine Lehrer eingetragen sind. Falls die Stunden einer Lehrer ausgewertet
        werden, wird hier höchstens nur diese Lehrer zurückgegeben.
        """
        if self._planart == "L":
            return [self._context] if not self.ausfall else []
        else:
            if s := self._tag_data("Le", "text"):
                return slice_aufzählung(s)
            return []

    @property
    def räume(self) -> list[str]:
        """Alle Räume der Stunde. Gibt `[]` zurück, wenn die Stunde entfällt oder
        keine Räume eingetragen sind. Falls die Stunden eines Raums ausgewertet
        werden, wird hier höchstens nur dieser Raum zurückgegeben.
        """
        if self._planart == "R":
            return [self._context] if not self.ausfall else []
        else:
            if s := self._tag_data("Ra", "text"):
                return slice_aufzählung(s)
            return []
            
    @property
    def fachgeändert(self) -> bool:
        "Ob das Fach der Stunde geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt."
        return "FaAe" in self._tag_data("Fa", "attrib")
    
    @property
    def lehrergeändert(self) -> bool:
        "Ob der Lehrer der Stunde geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt."
        return "LeAe" in self._tag_data("Le", "attrib") if self._planart != "L" else self.raumgeändert
    
    @property
    def raumgeändert(self) -> bool:
        "Ob der Raum der Stunde geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt."
        return "RaAe" in self._tag_data("Ra", "attrib") if self._planart != "R" else self.klassegeändert
    
    @property
    def klassegeändert(self) -> bool:
        "Ob die Klasse der Stunde geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt."
        if self._planart == "K":
            return self.raumgeändert
        elif self._planart == "L":
            return "LeAe" in self._tag_data("Le", "attrib")
        elif self._planart == "R":
            return "RaAe" in self._tag_data("Ra", "attrib")

    @property
    def geändert(self) -> bool:
        "Ob die Stunde in irgendeiner Weise geändert wurde. Ebenfalls `True`, wenn die Stunde entfällt"
        return self.fachgeändert or self.lehrergeändert or self.raumgeändert or self.klassegeändert

    @property
    def verlegt(self) -> bool:
        "Ob die Stunde hierher verlegt wurde"
        if (match := re.search(config.STUNDE_HERVERLEGT_PATTERN, self.info or "")):
            return True
        return False
    
    @property
    def kursnummer(self) -> int | None:
        """Nummer des Kurses der Stunde

        Kann `None` sein, wenn das Fach der Stunde geändert wurde, jedoch nicht, wenn
        die Stunde entfällt oder, beispielsweise wenn die Stunde eine Exkursion ist.
        
        Kursnummern können verwendet werden, um in den Kursen einer Klasse mehr
        Details zu einem Kurs zu erhalten, beispielsweise wenn eine Unterrichtsstunde
        ausfällt und Informationen wie Lehrer, Fach und Raum deswegen nicht verfügbar sind.
        """
        if nr := self._tag_data("Nr", "text"):
            if nr.endswith("+"): # Gemäß #44
                nr = nr[:-1]
            return int(nr)
        return None
    
    @property
    def info(self) -> str | None:
        "Zusätzliche Informationen zur Stunde"
        return self._tag_data("If", "text") or None

    @classmethod
    def new(cls,
        periode: int,
        beginn: time,
        ende: time,
        kursnummer: int | None = None,
        *,
        fach: str | None = None,
        fachmeta: str | None = None,
        fachgeändert: bool = False,
        lehrer: list[str] = [],
        räume: list[str] = [],
        klassen: list[str] = [],
        lehrergeändert: bool = False,
        raumgeändert: bool = False,
        klassegeändert: bool = False,
        info: str = None,
        planart: Literal["K", "L", "R"] = "K"
    )-> Stunde:
        # Falls die Planart K ist, muss ein Wert in klassen gesetzt sein, etc., sonst kommen leere Werte in die XML, was zu Fehlern bei der Interpretation durch vpmobil führen kann.
        Std = XML.Element("Std")
        add_Element(Std, "St", str(periode))
        add_Element(Std, "Beginn", beginn.strftime("%H:%M"))
        add_Element(Std, "Ende", ende.strftime("%H:%M"))
        add_Element(Std, "Nr", kursnummer)
        add_Element(Std, "If", info)
        add_Element(Std, "Fa", fach or "---", {"FaAe": "FaGeaendert"} if fachgeändert else {})
        add_Element(Std, "Ku2", fachmeta)
        add_Element(Std, "Le", config.AUFZÄHLUNGS_SEPARATOR.join(klassen if planart == "L" else lehrer), {"LeAe": "LeGeaendert"} if (klassegeändert if planart == "L" else lehrergeändert ) else {})
        add_Element(Std, "Ra", config.AUFZÄHLUNGS_SEPARATOR.join(klassen if planart == "R" else räume), {"RaAe": "RaGeaendert"} if (klassegeändert if planart == "L" else raumgeändert) else {})
        return cls(Std, planart, ((klassen if planart == "K" else lehrer if planart == "L" else räume) or [""])[0])
    

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Kurs                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Kurs(VpMobilPyModell):
    """Klasse die einen bestimmten Kurs repräsentiert.
    """

    def __repr__(self) -> str:
        return f"<'{self.kürzel}' bei '{self.lehrer}' (Kursnummer '{self.kursnummer}')>"
    
    @property
    def kursnummer(self) -> int:
        "Kursnummer des Kurses"
        if s := self._tag_data("UeNr", "text"):
            return int(s)
        return None # Error-Safe
    
    @property
    def kürzel(self) -> str | None:
        "Gruppenbezeichnung des Kurses. Falls keine vorhanden ist, wird das Fach zurückgegeben."
        return self._tag_data("UeNr", "attrib").get("UeGr", self.fach)
    
    @property
    def fach(self) -> str | None:
        "Fach des Kurses"
        return self._tag_data("UeNr", "attrib").get("UeFa", None)
    
    @property
    def lehrer(self) -> str | None:
        "Lehrer des Kurses"
        return self._tag_data("UeNr", "attrib").get("UeLe", None)

    @classmethod
    def new(cls, kursnummer: int, fach: str | None = None, lehrer: str | None = None, kürzel: str | None = None, planart: Literal["K", "L", "R"] = "K") -> Kurs:
        return cls(XML.fromstring(
            f"""<Ue><UeNr UeFa="{fach or ''}" UeLe="{lehrer or ''}" UeGr="{kürzel or ''}">{kursnummer}</UeNr></Ue>"""
        ), planart)