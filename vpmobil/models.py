from __future__ import annotations
from dataclasses import dataclass, field
from xml.etree import ElementTree as XML
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Literal, Any

from vpmobil.utils import prettyxml, slice_aufzählung
from vpmobil import config

@dataclass(init=True, eq=False)
class VpMobilPyModell():

    _data:    XML.Element            = field(init=True)
    _planart: Literal["K", "L", "R"] = field(init=True)

    def _data_value_safe_type(self, tag: str, attr: Literal["text", "attrib"]) -> str | dict | Literal[False]:
        "Gibt ein Attribut eines Untertags zurück.<br>Ist niemals `None`. Stattdessen wird `\"\"` oder `{}` zurückgegeben."
        element = self._data.find(tag)
        match attr:
            case "text":    return getattr(element, attr, "")
            case "attrib":  return getattr(element, attr, {})

    def as_dict(self) -> dict[str, Any]:
        """Gibt alle nicht versteckten Properties des Modells als Dictionary zurück und wandelt alle Datentypen in Primitives um, sodass das Dictionary beispielsweise in JSON modelliert werden kann.
        
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
                return tuple(apply_converter(v) for v in value)
            if isinstance(value, dict):
                return {k: apply_converter(v) for k, v in value.items()}

            for t, conv in converters.items():
                if isinstance(value, t):
                    return conv(value)

            return value

        result = {}
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name, None)
            if isinstance(attr, property):
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
    """Base-Class für Vertretungspläne.

    Beim Versuch einer Instanzierung wird automatisch eine Instanz von `VertretungsTag`, `LehrerVertretungsTag` oder `RaumVertretungsTag` zurückgegeben.

    Diese klasse kann mit `isinstance()` auch als Protokoll für die oben genannten Subklassen verwendet werden.
    """

    _data:    XML.ElementTree        = field(init=True)
    _planart: Literal["K", "L", "R"] = field(init=False, default=None)

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
                    raise ValueError(f"Planart muss eins von 'K', 'L' oder 'R' sein, nicht '{_data.find("Kopf/planart").text}'")
                
        return super().__new__(cls)
            
    def __post_init__(self):
        self._planart = self._data.find("Kopf/planart").text
            
    def __repr__(self):
        return f"<Vertretungsplan (Typ {self._planart}) vom {self.datum.strftime(r'%d.%m.%Y')}>"
        
    @property
    def zeitstempel(self) -> datetime | None:
        "Veröffentlichungszeitpunkt des Vertretungsplans"
        if s := self._data_value_safe_type("Kopf/zeitstempel", "text"):
            return datetime.strptime(s, r"%d.%m.%Y, %H:%M")
        return None
        
    @property
    def datei(self) -> str | None:
        "Dateiname der Quelldatei"
        return self._data_value_safe_type("Kopf/datei", "text") or None

    @property
    def datum(self) -> date | None:
        "Datum für das der Vertretungsplan gilt"
        import locale; locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

        if s := self._data_value_safe_type("Kopf/DatumPlan", "text"):
            return datetime.strptime(s, (r"%A, %d. %B %Y")).date()
        return None
    
    @property
    def freieTage(self) -> list[date]:
        "Im Vertretungsplan als frei markierte Tage"
        if freieTage := self._data.find("FreieTage"):
            return [
                datetime.strptime(ft.text, "%y%m%d").date()
                for ft in freieTage.findall("ft")
                if ft.text is not None
            ]
        return []
    
    @property
    def zusatzInfo(self) -> str | None:
        """Zusätzliche Informationen zum Tag<br>
        Kann Multiline sein
        """
        if zusatzInfo := self._data.find('ZusatzInfo'):
            return '\n'.join([
                ziZeile.text
                for ziZeile in zusatzInfo.findall('ZiZeile')
                if ziZeile.text
            ])
        return None
            
    @classmethod
    def fromfile(cls, pfad: Path | str) -> KlassenVertretungsTag | LehrerVertretungsTag | RaumVertretungsTag:
        """
        Erzeugt ein Vertretungsplan-Objekt aus einer XML-Vertretungsplandatei.

        Parameter
        ----------
        pfad: Path
            Dateipfad einer XML-Datei

        Raises
        ----------
        FileNotFoundError : Wenn die Datei nicht existiert
        ValueError : Wenn die Datei nicht gelesen werden kann
        """
        with open(pfad, encoding="utf-8-sig") as f:
            instance = cls(_data=XML.parse(f))
        return instance
    
    def saveasfile(self, pfad: Path | str = "./datei.xml", overwrite=True) -> None:
        """Speichert alle Daten des Tages als XML-Datei.

        Parameter
        ---------
        pfad : Path | str
            Der Dateipfad der zu erstellenden Datei
        overwrite : bool
            Ob die Datei überschrieben werden darf, falls sie bereits existiert

        Raises
        --------
        FileExistsError : Falls eine bereits existierende Datei überschrieben werden soll, obwohl `overwrite` `False` ist
        """

        xmlpretty = prettyxml(self._data)

        zielpfad = Path(pfad).resolve() if isinstance(pfad, str) else pfad.resolve()
        zielverzeichnis = zielpfad.parent
        zielverzeichnis.mkdir(parents=True, exist_ok=True)

        if zielpfad.exists() and not overwrite:
            raise FileExistsError(f"Die Datei '{zielpfad}' existiert bereits.")

        zielpfad.write_text(xmlpretty, encoding="utf-8")

    def _Kl_elemente(self) -> list[XML.Element]:
        if klassen := self._data.find('.//Klassen'):
            return [
                kl for kl in klassen.findall(".//Kl")
                if kl.find('Kurz') is not None
            ]
        return []

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                  KlassenVertretungsTag                                   │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class KlassenVertretungsTag(VertretungsTag):
    """Klasse die den Vertretungsplan an einem bestimmten Tag aus Sicht der Klassen repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: VpDay = vp.fetch()
    klasse = data["10a"]
    ```
    """

    def __getitem__(self, v) -> Klasse | None:
        return self.klassen.get(v)

    @property
    def lehrerKrank(self) -> list[str]:
        "Lehrer, die unplanmäßig keinen Unterricht haben"
        
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
            for element in self._Kl_elemente()
        }

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                   LehrerVertretungsTag                                   │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class LehrerVertretungsTag(VertretungsTag):
    """Klasse die den Vertretungsplan an einem bestimmten Tag aus Sicht der Lehrer repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: VpDay = vp.fetch()
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
            for element in self._Kl_elemente()
        }    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    RaumVertretungsTag                                    │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class RaumVertretungsTag(VertretungsTag):
    """Klasse die den Vertretungsplan an einem bestimmten Tag aus Sicht der Räume repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: VpDay = vp.fetch()
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
            for element in self._Kl_elemente()
        }    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                      KlasseLikeBase                                      │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class KlasseLikeBase(VpMobilPyModell):
    
    def __getitem__(self, v) -> list[Stunde]:
        return self.stundenInPeriode(v)
    
    @property
    def kürzel(self) -> str:
        return self._data.find('Kurz').text
    
    @property
    def stunden(self) -> dict[int, list[Stunde]]:
        """Alle Stunden an dem Tag als Dictionary<br>
        Die Schlüssel sind die Unterrichtsperioden, die Werte Listen von Unterrichsstunden
        """

        fin: dict[int, list[Stunde]] = {}
        pl = self._data.find("Pl")
        for std in pl.findall("Std"):
            stunde = Stunde(std, self._planart, self.kürzel)
            nr = stunde.periode
            if nr is not None:
                if fin.get(stunde.periode) is None:
                    fin[stunde.periode] = [stunde]
                else:
                    fin[stunde.periode].append(stunde)
        return fin

    def stundenInPeriode(self, periode: int) -> list[Stunde]:
        "Gibt die Stunden in einer bestimmten Unterrichtsperiode zurück."
        return self.stunden.get(periode) or []
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                           Klasse                                         │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Klasse(KlasseLikeBase):
    """Klasse, die den Vertretungsplan für eine bestimmte Klasse repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: Klasse = vpday.klasse("10a")
    stunden_zur_dritten = data[3]
    ```
    """

    def __repr__(self):
        return f"<Klasse '{self.kürzel}'>"
    
    @property
    def kurse(self) -> dict[str, Kurs]:
        "Kurse der Klasse als Dictionary<br>Die Keys sind die Kursnummern der Kurse" 
        if unterricht := self._data.find("Unterricht"):
            return {
                Kurs(ue, self._planart).kursnummer: Kurs(ue, self._planart)
                for ue in unterricht.findall("Ue")
            }
        return {}
    
    @property
    def klausuren(self) -> list[Klausur]:
        """Klausuren der Klasse"""
        if klausuren := self._data.find("Klausuren"):
            return [
                Klausur(klausur, self._planart)
                for klausur in klausuren.findall("Klausur")
            ]
        return []
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                           Lehrer                                         │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯
    
class Lehrer(KlasseLikeBase):
    """Klasse, die den Vertretungsplan für einen bestimmten Lehrer repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: Lehrer = vpday.lehrer("Ah")
    stunden_zur_dritten = data[3]
    ```
    """

    def __repr__(self):
        return f"<Lehrer '{self.kürzel}'>"
    
    @property
    def aufsichten(self) -> list[Aufsicht]:
        """Aufsichten des Lehrers"""
        if aufsichten := self._data.find("Aufsichten"):
            return [
                Aufsicht(aufsicht, self._planart)
                for aufsicht in aufsichten.findall("Aufsicht")
            ]
        return []

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                           Raum                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Raum(KlasseLikeBase):
    """Klasse, die den Vertretungsplan für einen bestimmten Raum repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: Raum = vpday.raum("E07")
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
        return self._data_value_safe_type("AuVorStunde", "text") or None
    
    @property
    def uhrzeit(self) -> time | None:
        "Uhrzeit der Aufsicht"
        if s := self._data_value_safe_type("AuUhrzeit", "text"):
            return datetime.strptime(s, "%H:%M").time()  
        return None
    
    @property
    def zeit(self) -> str | None:
        "Hinweis zum Zeitpunkt der Aufsicht"
        return self._data_value_safe_type("AuZeit", "text") or None
    
    @property
    def ort(self) -> str | None:
        "Hinweis zum Ort der Aufsicht"
        return self._data_value_safe_type("AuOrt", "text") or None

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
        return self._data_value_safe_type("KlKurs", "text") or None

    @property
    def lehrer(self) -> str | None:
        "Lehrer des Kurses für den die Klausur ansteht"
        return self._data_value_safe_type("KlKursleiter", "text") or None
    
    @property
    def periode(self) -> int | None:
        "Unterrichtsperiode, zu der die Klausur beginnt<br>Kann `0` sein"
        if s := self._data_value_safe_type("KlStunde", "text"):
            return int(s)
        return None
    
    @property
    def beginn(self) -> time | None:
        "Beginn der Klausur"
        if s := self._data_value_safe_type("KlBeginn", "text"):
            return datetime.strptime(s, "%H:%M").time()
        return None
    
    @property
    def dauer(self) -> timedelta | None:
        if s := self._data_value_safe_type("KlDauer", "text"):
            return timedelta(minutes=int(s))
        return None
    
    @property
    def info(self) -> str | None:
        "Zusätzliche Information zur Klausur"
        return self._data_value_safe_type("KlKinfo", "text") or None
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Stunde                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(eq=False)
class Stunde(VpMobilPyModell):
    """Klasse, die eine bestimmte Unterrichtsstunde repräsentiert.
    """

    _context: str = field(init=True)
    
    def __repr__(self):
        if self.ausfall:
            return f"<Ausfall: '{self.info}'>"
        return f"<'{", ".join(self.klassen)}' mit '{self.fach}' bei '{", ".join(self.lehrer)}' in '{", ".join(self.räume)}'>"
    
    @property
    def periode(self) -> int:
        "Unterrichtsperiode der Stunde<br>Kann `0` sein"
        return int(self._data.find("St").text)

    @property
    def beginn(self) -> time | None:
        "Beginn der Stunde"
        if s := self._data_value_safe_type("Beginn", "text"):
            return datetime.strptime(s, "%H:%M").time()  
        return None
    
    @property
    def ende(self) -> time | None:
        "Ende der Stunde"
        if s := self._data_value_safe_type("Ende", "text"):
            return datetime.strptime(s, "%H:%M").time() 
        return None
    
    @property
    def ausfall(self) -> bool:
        """Ob die Stunde entfällt<br>Ebenfalls `True`, falls Die Stundeninfo `"selbst"` enthält und Lehrer und Räume nicht vorhanden sind"""
        return self._data_value_safe_type("Fa", "text") == "---" or (self.info is not None and "selbst" in self.info and not self.räume)

    @property
    def fach(self) -> str | None:
        """Fach der Stunde<br>
        Gibt `None` zurück, wenn die Stunde entfällt

        Es kann sein, dass nicht das wirkliche Fach sondern die Kursbezeichnung zurückgegeben wird. Stattdessen `klasse.kurs(stunde.kursnummer).fach` verwenden.<br>
        Bei Unsicherheit mit Fallback:
        ```
        stunde.fach if klasse.kurs(stunde.kursnummer) is None else klasse.kurs(stunde.kursnummer).fach
        ```
        """
        if (s := self._data_value_safe_type("Fa", "text")) != "---":
            return s
        return None

    @property
    def klassen(self) -> list[str]:
        """Alle Klassen der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Klassen eingetragen sind
        """
        if self._planart == "K":
            return [self._context]
        elif self._planart == "R":
            return slice_aufzählung(self._data.find("Ra").text) if self._data_value_safe_type("Ra", "text") else []
        elif self._planart == "L":
            return slice_aufzählung(self._data.find("Le").text) if self._data_value_safe_type("Le", "text") else []

        
    @property
    def lehrer(self) -> list[str]:
        """Alle Lehrer der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Lehrer eingetragen sind
        """
        if self._planart == "L":
            return [self._context]
        else:
            if s := self._data_value_safe_type("Le", "text"):
                return slice_aufzählung(s)
            return []

        
    @property
    def räume(self) -> list[str]:
        """Räume der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Räume eingetragen sind
        """
        if self._planart == "R":
            return [self._context]
        else:
            if s := self._data_value_safe_type("Ra", "text"):
                return slice_aufzählung(s)
            return []
            
    @property
    def fachgeändert(self) -> bool:
        "Ob eine Änderung des Fachs für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "FaAe" in self._data_value_safe_type("Fa", "attrib")
    
    @property
    def lehrergeändert(self) -> bool | None:
        "Ob eine Änderung des Lehrers für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt<br>Ist None, falls die Stunde aus einem Lehrerplan kommt"
        return "LeAe" in self._data_value_safe_type("Le", "attrib") if self._planart != "L" else None
    
    @property
    def raumgeändert(self) -> bool | None:
        "Ob eine Änderung des Raums für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt<br>Ist None, falls die Stunde aus einem Raumplan kommt"
        return "RaAe" in self._data_value_safe_type("Ra", "attrib") if self._planart != "R" else None
    
    @property
    def klassegeändert(self) -> bool | None:
        "Ob eine Änderung der Klasse für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt<br>Ist None, falls die Stunde aus einem Klassenplan kommt"
        if self._planart == "K":
            return None
        elif self._planart == "L":
            return "LeAe" in self._data_value_safe_type("Le", "attrib")
        elif self._planart == "R":
            return "RaAe" in self._data_value_safe_type("Ra", "attrib")

    @property
    def geändert(self) -> bool:
        "Ob eine Änderung im Plan vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return bool(self.fachgeändert or self.lehrergeändert or self.raumgeändert or self.klassegeändert)

    @property
    def kursnummer(self) -> int | None:
        """Nummer des Kurses der Stunde

        Kann `None` sein, wenn das Fach der Stunde geändert wurde, jedoch nicht, wenn die Stunde entfällt.<br>
        Kann `None` sein, beispielsweise wenn die Stunde eine Exkursion ist.
        
        Kursnummern können verwendet werden, um in den Kursen einer Klasse mehr Details zu einem Kurs zu erhalten, beispielsweise, wenn eine Unterrichtsstunde ausfällt und Informationen wie Lehrer, Fach und Raum deswegen nicht verfügbar sind.
        """
        if nr := self._data_value_safe_type("Nr", "text"):
            if nr.endswith("+"): # Gemäß #44
                nr = nr[:-1]
            return int(nr)
        return None
    
    @property
    def info(self) -> str | None:
        "Zusätzliche Information zur Stunde"
        return self._data_value_safe_type("If", "text") or None
            
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Kurs                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Kurs(VpMobilPyModell):
    """Klasse die einen bestimmten Kurs repräsentiert.
    """

    def __repr__(self) -> str:
        return f"<'{self.kürzel}' bei '{self.lehrer}' (Kursnummer '{self.kursnummer}')>"
    
    @property
    def kürzel(self) -> str | None:
        "Gruppenbezeichnung des Kurses<br>Gibt als Fallback das Fach zurück"
        return self._data_value_safe_type("UeNr", "attrib").get("UeGr", self.fach)
    
    @property
    def lehrer(self) -> str | None:
        "Lehrer des Kurses"
        return self._data_value_safe_type("UeNr", "attrib").get("UeLe", None)
    
    @property
    def fach(self) -> str | None:
        "Fach des Kurses"
        return self._data_value_safe_type("UeNr", "attrib").get("UeFa", None)

    @property
    def kursnummer(self) -> int:
        "Kursnummer des Kurses"
        if s := self._data_value_safe_type("UeNr", "text"):
            return int(s)
        return None
    

VertretungsTagType = KlassenVertretungsTag | RaumVertretungsTag | LehrerVertretungsTag
KlasseLikeType = Klasse | Lehrer | Raum