from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as XML
from typing import Literal, Any
from datetime import datetime, date, time
import re

from vpmobil.utils import prettyxml

@dataclass(init=True)
class VpmobilPyModell():

    _data:    XML.Element            = field(init=True)
    _planart: Literal["K", "L", "R"] = field(init=True)

    def _data_safe_value(self, tag: str, attr: Literal["text", "attrib"]) -> str | dict | None:
        "Gibt `None`-safe das Attribut eines Untertags zurück.<br>Ist `None`, wenn `tag` nichts existiert, `attr` `None` oder `""` ist"
        return None if getattr(self._data.find(tag), attr, None) == "" else getattr(self._data.find(tag), attr, None)

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                   VertretungsTagBase                                     │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VertretungsTagBase(VpmobilPyModell):
    """Base-Class für Vertretungspläne an einem bestimmten Tag.

    Beim Versuch einer Instanzierung wird automatisch eine Instanz von `VertretungsTag`, `LehrerVertretungsTag` oder `RaumVertretungsTag` zurückgegeben.
    """

    _data:    XML.ElementTree        = field(init=True)
    _planart: Literal["K", "L", "R"] = field(init=False, default=None)

    def __new__(cls, _data: XML.ElementTree):
        if _data.find(".//planart") is None or _data.find(".//planart").text is None:
            raise ValueError
        
        match _data.find(".//planart").text:
            case "K":
                return VertretungsTag(_data)
            case "L":
                return LehrerVertretungsTag(_data)
            case "R":
                return RaumVertretungsTag(_data)
            case _:
                raise ValueError
            
    def __post_init__(self):
        self._planart = self._data.find("Kopf/planart").text
            
    def __repr__(self):
        return f"<Vertretungsplan (Typ {self._planart}) vom {self.datum.strftime('%d.%m.%Y')}>"
        
    @property
    def zeitstempel(self) -> datetime | None:
        "Veröffentlichungszeitpunkt des Vertretungsplans"
        element = self._data.find('Kopf/zeitstempel')
        if element is None or not element.text:
            return None
        return datetime.strptime(element.text, "%d.%m.%Y, %H:%M")
        
    @property
    def datei(self) -> str | None:
        "Dateiname der Quelldatei"
        element = self._data.find('Kopf/datei')
        if element is None or not element.text:
            return None
        return element.text

    @property
    def datum(self) -> date | None:
        "Datum für das der Vertretungsplan gilt"
        if match := re.search(r"(\d{4})(\d{2})(\d{2})", self.datei):
            year, month, day = map(int, match.groups())
            return date(year, month, day)
        return None
    
    @property
    def freieTage(self) -> list[date] | None:
        "Im Vertretungsplan als frei markierte Tage"

        freieTage = self._data.find("FreieTage")
        if freieTage is None:
            return None
        
        freieTageList: list[date] = []
        for ft in freieTage.findall("ft"):
            if ft.text is not None:
                freieTageList.append(datetime.strptime(ft.text, "%y%m%d").date())
        return freieTageList
            
    @classmethod
    def fromfile(cls, pfad: Path) -> VertretungsTag | LehrerVertretungsTag | RaumVertretungsTag:
        """
        Erzeugt ein VertretungsTag-Objekt aus einer XML-Vertretungsplandatei

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
        """Speichert alle Daten des Tages als XML-Datei

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

    def _elemente_Klassen(self) -> list[XML.Element] | None:
        klassen: list[XML.Element] = []
        klassen_elemente = self._data.findall('.//Kl')
        if klassen_elemente is not []:
            for kl in klassen_elemente:
                if kl.find('Kurz') is not None:
                    klassen.append(kl)
            return klassen
        return None

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                      VertretungsTag                                      │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VertretungsTag(VertretungsTagBase):

    @property
    def lehrerKrank(self) -> list[str]:
        "Aller Lehrer, die unplanmäßig keinen Unterricht haben"
        
        lehrerMitUnterricht: set[str] = set()
        lehrerVielleichtKrank: set[str] = set()

        for klasse in self.klassen:
            for stunde in [stunde for stunden in klasse.stundenHeute.values() for stunde in stunden]:

                if stunde.ausfall and klasse.kurs(stunde.kursnummer) is not None:
                    lehrerVielleichtKrank.add(klasse.kurs(stunde.kursnummer).lehrer)

                elif stunde.lehrergeändert:
                    if stunde.lehrer is not None:
                        lehrerMitUnterricht.update(stunde.lehrer)
                    if klasse.kurs(stunde.kursnummer) is not None:
                        lehrerVielleichtKrank.add(klasse.kurs(stunde.kursnummer).lehrer)

                elif not stunde.ausfall and not stunde.lehrergeändert:
                    if stunde.lehrer is not None:
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
        "Im Vertretungsplan hinterlegte Klassen"
        return [Klasse(element, self._planart) for element in (self._elemente_Klassen() or [])]
    
    def klasse(self, kürzel: str) -> Klasse | None:
        "Gibt die Klasse zurück, deren Tag `<Kurz>` gleich `kürzel` ist"

        for kl in self.klassen:
            if kl.kürzel == kürzel:
                return kl
        return None

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                   LehrerVertretungsTag                                   │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class LehrerVertretungsTag(VertretungsTagBase):

    @property
    def lehrer(self) -> list[Lehrer]:
        "Im Vertretungsplan hinterlegte Klassen"
        return [Lehrer(element, self._planart) for element in (self._elemente_Klassen() or [])]
    
    def get_lehrer(self, kürzel: str) -> Lehrer | None:
        "Gibt den Lehrer zurück, dessen Tag `<Kurz>` gleich `kürzel` ist"

        for le in self.lehrer:
            if le.kürzel == kürzel:
                return le
        return None
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    RaumVertretungsTag                                    │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class RaumVertretungsTag(VertretungsTagBase):
    
    @property
    def räume(self) -> list[Raum]:
        "Im Vertretungsplan hinterlegte Klassen"
        return [Raum(element, self._planart) for element in (self._elemente_Klassen() or [])]
    
    def raum(self, kürzel: str) -> Raum | None:
        "Gibt den Lehrer zurück, dessen Tag `<Kurz>` gleich `kürzel` ist"

        for ra in self.räume:
            if ra.kürzel == kürzel:
                return ra
        return None
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                      KlasseLikeBase                                      │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class KlasseLikeBase(VpmobilPyModell):
    
    @property
    def kürzel(self) -> str:
        return self._data.find('Kurz').text
    
    @property
    def stundenHeute(self) -> dict[int, list[Stunde]]:
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

    def stundenHeuteInPeriode(self, periode: int) -> list[Stunde]:
        "Gibt die Stunden an dem Tag in einer bestimmten Unterrichtsperiode zurück"
        return self.stundenHeute.get(periode) or []
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                           Klasse                                         │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Klasse(KlasseLikeBase):
    """Klasse, die den Vertretungsplan für eine bestimmte Klasse an einem bestimmten Tag repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: Klasse = vpday.klasse("10a")
    stunden_zur_dritten = data[3]
    ```
    """

    @property
    def kurse(self) -> list[Kurs]:
        "Alle im Plan vermerkten Kurse, die die Klasse hat"
        fin: list[Kurs] = []
        unterricht = self._data.find("Unterricht")
        for ue in unterricht.findall("Ue"):
            fin.append(Kurs(ue, self._planart))
        return fin
    
    def kurs(self, kursnummer: int) -> Kurs | None:
        "Gibt den Kurs der Klasse mit der Kursnummer `kursnummer` zurück"
        for kurs in self.kurse:
            if kurs.kursnummer == kursnummer:
                return kurs
        return None
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                           Lehrer                                         │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯
    
class Lehrer(KlasseLikeBase):
    
    @property
    def aufsichten(self) -> list[Aufsicht]:
        """Alle Aufsichten an dem Tag als Dictionary<br>
        Die Schlüssel sind die Unterrichtsperioden, die Werte Listen von Unterrichsstunden
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
    ...

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Aufsicht                                         │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Aufsicht(VpmobilPyModell):

    @property
    def vorStunde(self) -> int:
        return self._data_safe_value("AuVorStunde", "text")
    
    @property
    def uhrzeit(self) -> time:
        "Uhrzeit der Aufsicht"
        return datetime.strptime(self._data.find("AuUhrzeit").text, "%H:%M").time() if self._data_safe_value("AuUhrzeit", "text") is not None else None
    
    @property
    def zeit(self) -> str:
        "Hinweis zum Zeitpunkt der Aufsicht"
        return self._data_safe_value("AuZeit", "text")
    
    @property
    def ort(self) -> str:
        "Hinweis zum Ort der Aufsicht"
        return self._data_safe_value("AuOrt", "text")

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Stunde                                          │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Stunde(VpmobilPyModell):

    _quelle: str = field(init=True)
    
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
        return datetime.strptime(self._data.find("Beginn").text, "%H:%M").time() if self._data_safe_value("Beginn", "text") is not None else None
    
    @property
    def ende(self) -> time:
        "Ende der Stunde"
        return datetime.strptime(self._data.find("Ende").text, "%H:%M").time() if self._data_safe_value("Ende", "text") is not None else None
    
    @property
    def ausfall(self) -> bool:
        "Ob die Stunde entfällt"
        return self._data_safe_value("Fa", "text") == "---"

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
        return self._data_safe_value("Fa", "text") if self._data_safe_value("Fa", "text") != "---" else None

    @property
    def klassen(self) -> str | None:
        """Alle Klassen der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Klassen eingetragen sind
        """
        if self._planart == "K":
            return self._quelle
        elif self._planart == "R":
            return self._data.find("Ra").text.split(" ") if self._data_safe_value("Ra", "text") is not None else []
        elif self._planart == "L":
            return self._data.find("Le").text.split(" ") if self._data_safe_value("Le", "text") is not None else []

        
    @property
    def lehrer(self) -> list[str]:
        """Alle Lehrer der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Lehrer eingetragen sind
        """
        if self._planart == "L":
            return self._quelle
        else:
            return self._data.find("Le").text.split(" ") if self._data_safe_value("Le", "text") is not None else []

        
    @property
    def räume(self) -> list[str]:
        """Räume der Stunde<br>
        Gibt `[]` zurück, wenn die Stunde entfällt oder keine Räume eingetragen sind
        """
        if self._planart == "R":
            return self._quelle
        else:
            return self._data.find("Ra").text.split(" ") if self._data_safe_value("Ra", "text") is not None else []
        
    @property
    def fachgeändert(self) -> bool:
        "Ob eine Änderung des Fachs für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "FaAe" in self._data_safe_value("Fa", "attrib")
    
    @property
    def lehrergeändert(self) -> bool:
        "Ob eine Änderung des Lehrers für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "LeAe" in self._data_safe_value("Le", "attrib") if self._planart != "L" else False
    
    @property
    def raumgeändert(self) -> bool:
        "Ob eine Änderung des Raums für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "RaAe" in self._data_safe_value("Ra", "attrib") if self._planart != "R" else False
    
    @property
    def klassegeändert(self) -> bool:
        "Ob eine Änderung der Klasse für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        if self._planart == "K":
            return False
        elif self._planart == "L":
            return "LeAe" in self._data_safe_value("Le", "attrib")
        elif self._planart == "R":
            return "RaAe" in self._data_safe_value("Ra", "attrib")

    @property
    def geändert(self) -> bool:
        "Ob eine Änderung im Plan vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return self.fachgeändert or self.lehrergeändert or self.raumgeändert or self.klassegeändert

    @property
    def kursnummer(self) -> int | None:
        """Nummer des Kurses der Stunde<br>
        Kann `None` sein, wenn das Fach der Stunde geändert wurde, jedoch nicht, wenn die Stunde entfällt.<br>
        Kann `None` sein, beispielsweise wenn die Stunde eine Exkursion ist.
        
        Kursnummern können verwendet werden, um in den Kursen einer Klasse mehr Details zu einem Kurs zu erhalten, beispielsweise, wenn eine Unterrichtsstunde ausfällt und Informationen wie Lehrer, Fach und Raum deswegen nicht verfügbar sind.
        """
        return int(self._data.find("Nr").text) if self._data_safe_value("Nr", "text") is not None else None
    
    @property
    def info(self) -> str | None:
        "Zusätzliche Information der Stunde"
        return self._data_safe_value("If", "text")
        
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                          Kurs                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Kurs(VpmobilPyModell):
    """Klasse die einen bestimmten Kurs repräsentiert.
    """

    def __repr__(self) -> str:
        return f"<'{self.fach}' bei '{self.lehrer}', Gruppe '{self.gruppe or '-'}' (Kursnummer '{self.kursnummer}')>"
    
    @property
    def lehrer(self) -> str | None:
        "Lehrer des Kurses"
        return self._data_safe_value("UeNr", "attrib").get("UeLe", None)
    
    @property
    def fach(self) -> str | None:
        "Fach des Kurses"
        return self._data_safe_value("UeNr", "attrib").get("UeFa", None)
    
    @property
    def gruppe(self) -> str | None:
        "Gruppenbezeichnung des Kurses"
        return self._data_safe_value("UeNr", "attrib").get("UeGr", None)

    @property
    def kursnummer(self) -> int:
        "Kursnummer des Kurses"
        return int(self._data_safe_value("UeNr", "text")) if self._data_safe_value("UeNr", "text") is not None else None