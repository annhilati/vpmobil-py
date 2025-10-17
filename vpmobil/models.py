from __future__ import annotations
from dataclasses import dataclass, field
from xml.etree import ElementTree as XML
from datetime import datetime, date, time
from pathlib import Path
from typing import Literal, Any
import re

from vpmobil.utils import prettyxml
from vpmobil import config

@dataclass(init=True, eq=False)
class VpmobilPyModell():

    _data:    XML.Element            = field(init=True)
    _planart: Literal["K", "L", "R"] = field(init=True)

    def _data_value_safe_type(self, tag: str, attr: Literal["text", "attrib"]) -> str | dict | Literal[False]:
        "Gibt ein Attribut eines Untertags zurück.<br>Ist niemals `None`. Stattdessen wird `\"\"` oder `{}` zurückgegeben."
        element = self._data.find(tag)
        match attr:
            case "text":    return getattr(element, attr, "")
            case "attrib":  return getattr(element, attr, {})

    def _as_dict(self) -> dict[str, Any]:
        """Gibt alle Properties als Dict zurück, wendet bei Bedarf Typkonverter an."""

        converters = {
            datetime:   lambda d: d.strftime("%d.%m.%Y:%H:%M"),
            time:       lambda d: d.strftime("%H:%M"),
            date:       lambda d: d.strftime("%d.%m.%Y"),
        }

        def apply_converter(value: Any) -> Any:
            # Rekursion für Listen, Tupel, Dictionaries
            if isinstance(value, list):
                return [apply_converter(v) for v in value]
            if isinstance(value, tuple):
                return tuple(apply_converter(v) for v in value)
            if isinstance(value, dict):
                return {k: apply_converter(v) for k, v in value.items()}

            # Rekursive Behandlung eigener Modelle
            if isinstance(value, VpmobilPyModell):
                return value._as_dict()

            # Typkonverter anwenden
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
        return result


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                   VertretungsTagBase                                     │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(eq=False) # Dunder neu generieren
class MobdatenBase(VpmobilPyModell):
    """Base-Class für Vertretungspläne.

    Beim Versuch einer Instanzierung wird automatisch eine Instanz von `VertretungsTag`, `LehrerVertretungsTag` oder `RaumVertretungsTag` zurückgegeben.

    Diese klasse kann mit `isinstance()` auch als Protokoll für die oben genannten Subklassen verwendet werden.
    """

    _data:    XML.ElementTree        = field(init=True)
    _planart: Literal["K", "L", "R"] = field(init=False, default=None)

    def __new__(cls, _data: XML.ElementTree):
        if cls is MobdatenBase:
            if _data.find("Kopf/planart") is None or _data.find("Kopf/planart").text is None:
                raise ValueError("XML-Quelldaten sind unbekannt formatiert")
            
            match _data.find("Kopf/planart").text:
                case "K":
                    return VertretungsTag(_data)
                case "L":
                    return VertretungsTagLehrer(_data)
                case "R":
                    return VertretungsTagRäume(_data)
                case _:
                    raise ValueError(f"Planart muss eins von 'K', 'L' oder 'R' sein, nicht '{_data.find("Kopf/planart").text}'")
                
        return super().__new__(cls)
            
    def __post_init__(self):
        self._planart = self._data.find("Kopf/planart").text
            
    def __repr__(self):
        return f"<Vertretungsplan (Typ {self._planart}) vom {self.datum.strftime('%d.%m.%Y')}>"
        
    @property
    def zeitstempel(self) -> datetime | None:
        "Veröffentlichungszeitpunkt des Vertretungsplans"
        if self._data_value_safe_type("Kopf/zeitstempel", "text"):
            return datetime.strptime(self._data.find("Kopf/zeitstempel").text, "%d.%m.%Y, %H:%M")
        return None
        
    @property
    def datei(self) -> str | None:
        "Dateiname der Quelldatei"
        return self._data_value_safe_type("Kopf/datei", "text") or None

    @property
    def datum(self) -> date | None:
        "Datum für das der Vertretungsplan gilt"
        if match := re.search(r"(\d{4})(\d{2})(\d{2})", self.datei):
            year, month, day = map(int, match.groups())
            return date(year, month, day)
        return None
    
    @property
    def freieTage(self) -> list[date]:
        "Im Vertretungsplan als frei markierte Tage"

        freieTage = self._data.find("FreieTage")
        if freieTage is not None:
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
        ziZeilen = [
            ziZeile.text
            for zusatzInfo in self._data.findall('.//ZusatzInfo')
            for ziZeile in zusatzInfo.findall('.//ZiZeile')
            if ziZeile.text
        ]
        return '\n'.join(ziZeilen) if ziZeilen else None
            
    @classmethod
    def fromfile(cls, pfad: Path) -> VertretungsTag | VertretungsTagLehrer | VertretungsTagRäume:
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
        with open(pfad) as f:
            instance = cls(_data=XML.parse(f))
        return instance
    
    def saveasfile(self, pfad: Path | str = "./datei.xml", overwrite=False) -> None:
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

    def _elemente_Klassen(self) -> list[XML.Element]:
        klassen: list[XML.Element] = []
        klassen_elemente = self._data.findall('.//Kl')
        if klassen_elemente is not []:
            for kl in klassen_elemente:
                if kl.find('Kurz') is not None:
                    klassen.append(kl)
            return klassen
        return []

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                      VertretungsTag                                      │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VertretungsTag(MobdatenBase):
    """Klasse die den Vertretungsplan an einem bestimmten Tag aus Sicht der Klassen repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: VpDay = vp.fetch()
    klasse = data["10a"]
    ```
    """

    def __getitem__(self, v) -> Klasse | None:
        return self.klasse(v)

    @property
    def lehrerKrank(self) -> list[str]:
        "Lehrer, die unplanmäßig keinen Unterricht haben"
        
        lehrerMitUnterricht: set[str] = set()
        lehrerVielleichtKrank: set[str] = set()

        for klasse in self.klassen:
            for stunde in [stunde for stunden in klasse.stunden.values() for stunde in stunden]:

                if stunde.ausfall and klasse.kurs(stunde.kursnummer) is not None:
                    lehrerVielleichtKrank.add(klasse.kurs(stunde.kursnummer).lehrer)

                elif stunde.lehrergeändert:
                    if len(stunde.lehrer) > 0:
                        lehrerMitUnterricht.update(stunde.lehrer)
                    if klasse.kurs(stunde.kursnummer) is not None:
                        lehrerVielleichtKrank.add(klasse.kurs(stunde.kursnummer).lehrer)

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
    def klassen(self) -> list[Klasse]:
        "Im Vertretungsplan beschriebene Klassen"
        return [Klasse(element, self._planart) for element in self._elemente_Klassen()]
    
    def klasse(self, kürzel: str) -> Klasse | None:
        "Gibt die Klasse mit der Bezeichnung `kürzel` zurück."
        for kl in self.klassen:
            if kl.kürzel == kürzel:
                return kl
        return None

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                   LehrerVertretungsTag                                   │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VertretungsTagLehrer(MobdatenBase):
    """Klasse die den Vertretungsplan an einem bestimmten Tag aus Sicht der Lehrer repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: VpDay = vp.fetch()
    lehrer = data["Ah"]
    ```
    """

    def __getitem__(self, v) -> Klasse | None:
        return self.get_lehrer(v)

    @property
    def lehrer(self) -> list[Lehrer]:
        "Im Vertretungsplan beschriebene Lehrer"
        return [Lehrer(element, self._planart) for element in self._elemente_Klassen()]
    
    def get_lehrer(self, kürzel: str) -> Lehrer | None:
        "Gibt den Lehrer mit der Abkürzung `kürzel` zurück."
        for le in self.lehrer:
            if le.kürzel == kürzel:
                return le
        return None
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    RaumVertretungsTag                                    │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VertretungsTagRäume(MobdatenBase):
    """Klasse die den Vertretungsplan an einem bestimmten Tag aus Sicht der Räume repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: VpDay = vp.fetch()
    raum = data["E07"]
    ```
    """

    def __getitem__(self, v) -> Klasse | None:
        return self.raum(v)
    
    @property
    def räume(self) -> list[Raum]:
        "Im Vertretungsplan beschriebene Räume"
        return [Raum(element, self._planart) for element in self._elemente_Klassen()]

    def raum(self, kürzel: str) -> Raum | None:
        "Gibt den Raum mit der Bezeichnung `kürzel` zurück."
        for ra in self.räume:
            if ra.kürzel == kürzel:
                return ra
        return None
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                      KlasseLikeBase                                      │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class KlasseLikeBase(VpmobilPyModell):
    
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
    def kurse(self) -> list[Kurs]:
        "Kurse der Klasse"
        fin: list[Kurs] = []
        unterricht = self._data.find("Unterricht")
        for ue in unterricht.findall("Ue"):
            fin.append(Kurs(ue, self._planart))
        return fin
    
    def kurs(self, kursnummer: int) -> Kurs | None:
        "Gibt den Kurs der Klasse mit der Kursnummer `kursnummer` zurück."
        for kurs in self.kurse:
            if kurs.kursnummer == kursnummer:
                return kurs
        return None
    
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
        """Aufsichten des Lehrers
        """
        fin: list[Stunde] = []
        aufsichten = self._data.find("Aufsichten")
        for aufsicht in aufsichten.findall("Aufsicht"):
            fin.append(Aufsicht(aufsicht, self._planart))
        return fin

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

class Aufsicht(VpmobilPyModell):
    """Klasse, die eine Lehreraufsicht repräsentiert.
    """

    @property
    def vorStunde(self) -> int | None:
        "Unterrichtsperiode, vor der die Aufsicht stattfindet"
        return self._data_value_safe_type("AuVorStunde", "text") or None
    
    @property
    def uhrzeit(self) -> time | None:
        "Uhrzeit der Aufsicht"
        if self._data_value_safe_type("AuUhrzeit", "text"):
            return datetime.strptime(self._data.find("AuUhrzeit").text, "%H:%M").time()  
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
# │                                          Stunde                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass(eq=False)
class Stunde(VpmobilPyModell):
    """Klasse, die eine bestimmte Unterrichtsstunde repräsentiert.
    """

    _context: str = field(init=True)
    
    def __repr__(self):
        if self.ausfall:
            return f"<Ausfall: '{self.info}'>"
        return f"<'{self.fach}' bei '{", ".join(self.lehrer)}' in '{", ".join(self.räume)}'>"
    
    @property
    def periode(self) -> int:
        "Unterrichtsperiode der Stunde"
        return int(self._data.find("St").text)

    @property
    def beginn(self) -> time:
        "Beginn der Stunde"
        if self._data_value_safe_type("Beginn", "text"):
            return datetime.strptime(self._data.find("Beginn").text, "%H:%M").time()  
        return None
    
    @property
    def ende(self) -> time:
        "Ende der Stunde"
        if self._data_value_safe_type("Ende", "text"):
            return datetime.strptime(self._data.find("Ende").text, "%H:%M").time() 
        return None
    
    @property
    def ausfall(self) -> bool:
        "Ob die Stunde entfällt"
        return self._data_value_safe_type("Fa", "text") == "---"

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
        if self._data_value_safe_type("Fa", "text") != "---":
            return self._data_value_safe_type("Fa", "text")
        return None

    @property
    def klassen(self) -> list[str]:
        """Alle Klassen der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Klassen eingetragen sind
        """
        if self._planart == "K":
            return self._context
        elif self._planart == "R":
            return self._data.find("Ra").text.split(config.SEPARATOR) if self._data_value_safe_type("Ra", "text") else []
        elif self._planart == "L":
            return self._data.find("Le").text.split(config.SEPARATOR) if self._data_value_safe_type("Le", "text") else []

        
    @property
    def lehrer(self) -> list[str]:
        """Alle Lehrer der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Lehrer eingetragen sind
        """
        if self._planart == "L":
            return self._context
        else:
            if self._data_value_safe_type("Le", "text"):
                return self._data.find("Le").text.split(config.SEPARATOR)
            return []

        
    @property
    def räume(self) -> list[str]:
        """Räume der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Räume eingetragen sind
        """
        if self._planart == "R":
            return self._context
        else:
            if self._data_value_safe_type("Ra", "text"):
                return self._data.find("Ra").text.split(config.SEPARATOR) 
            return []
            
    @property
    def fachgeändert(self) -> bool:
        "Ob eine Änderung des Fachs für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "FaAe" in self._data_value_safe_type("Fa", "attrib")
    
    @property
    def lehrergeändert(self) -> bool:
        "Ob eine Änderung des Lehrers für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "LeAe" in self._data_value_safe_type("Le", "attrib") if self._planart != "L" else False
    
    @property
    def raumgeändert(self) -> bool:
        "Ob eine Änderung des Raums für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "RaAe" in self._data_value_safe_type("Ra", "attrib") if self._planart != "R" else False
    
    @property
    def klassegeändert(self) -> bool:
        "Ob eine Änderung der Klasse für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        if self._planart == "K":
            return False
        elif self._planart == "L":
            return "LeAe" in self._data_value_safe_type("Le", "attrib")
        elif self._planart == "R":
            return "RaAe" in self._data_value_safe_type("Ra", "attrib")

    @property
    def geändert(self) -> bool:
        "Ob eine Änderung im Plan vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return self.fachgeändert or self.lehrergeändert or self.raumgeändert or self.klassegeändert

    @property
    def kursnummer(self) -> int | None:
        """Nummer des Kurses der Stunde

        Kann `None` sein, wenn das Fach der Stunde geändert wurde, jedoch nicht, wenn die Stunde entfällt.<br>
        Kann `None` sein, beispielsweise wenn die Stunde eine Exkursion ist.
        
        Kursnummern können verwendet werden, um in den Kursen einer Klasse mehr Details zu einem Kurs zu erhalten, beispielsweise, wenn eine Unterrichtsstunde ausfällt und Informationen wie Lehrer, Fach und Raum deswegen nicht verfügbar sind.
        """
        if self._data_value_safe_type("Nr", "text"):
            return int(self._data.find("Nr").text)
        return None
    
    @property
    def info(self) -> str | None:
        "Zusätzliche Information der Stunde"
        return self._data_value_safe_type("If", "text") or None
        
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Kurs                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Kurs(VpmobilPyModell):
    """Klasse die einen bestimmten Kurs repräsentiert.
    """

    def __repr__(self) -> str:
        return f"<'{self.fach}' bei '{self.lehrer}', Gruppe '{self.kürzel or '-'}' (Kursnummer '{self.kursnummer}')>"
    
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
        if self._data_value_safe_type("UeNr", "text"):
            return int(self._data_value_safe_type("UeNr", "text"))
        return None