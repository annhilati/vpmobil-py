from __future__ import annotations

import xml.etree.ElementTree as XML
import re

from pathlib import Path
from datetime import datetime, date, time
from dataclasses import dataclass

from vpmobil.utils import prettyxml

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    VertretungsTag                                        │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class VertretungsTag():
    """Klasse die den Vertretungsplan an einem bestimmten Tag repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: VpDay = vp.fetch()
    klasse = data["10a"]
    ```
    """

    _data: XML.ElementTree

    def __post_init__(self):
        if self._data.find(".//planart") is None or self._data.find(".//planart").text != "K":
            raise ValueError("VpDay unterstützt nur Indiware-Vertretungspläne des Typs 'K'")

    def __getitem__(self, v) -> Klasse:
        return self.klasse(v)
        
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
    def zusatzInfo(self) -> str | None:
        """Zusätzliche Informationen zum Tag<br>
        Kann Multiline sein
        """
        ziZeilen = []
        for zusatzInfo in self._data.findall('.//ZusatzInfo'):
            for ziZeile in zusatzInfo.findall('.//ZiZeile'):
                if ziZeile.text:
                    ziZeilen.append(ziZeile.text)
        return '\n'.join(ziZeilen) if ziZeilen else None

    def __repr__(self):
        return f"<Vertretungsplan vom {self.datum.strftime('%d.%m.%Y')}>"

    @property
    def klassen(self) -> list[Klasse] | None:
        "Im Vertretungsplan hinterlegte Klassen"
        klassen: list[Klasse] = []
        klassen_elemente = self._data.findall('.//Kl')
        if klassen_elemente is not []:
            for kl in klassen_elemente:
                if kl.find('Kurz') is not None:
                    klassen.append(Klasse(_data=kl))
            return klassen
        return None

    def klasse(self, kürzel: str) -> Klasse | None:
        "Gibt die Klasse zurück, deren Tag `<Kurz>` gleich `kürzel` ist"

        klassen = self.klassen
        for kl in klassen:
            if kl.kürzel == kürzel:
                return kl
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

    @property
    def lehrerKrank(self) -> list[str]:
        "Aller Lehrer, die unplanmäßig keinen Unterricht haben"
        
        lehrerMitUnterricht: set[str] = set()
        lehrerVielleichtKrank: set[str] = set()

        for klasse in self.klassen:
            for stunde in [stunde for stunden in klasse.stundenHeute.values() for stunde in stunden]:
                if stunde.ausfall:
                    lehrerVielleichtKrank.add(klasse.kurs(stunde.kursnummer).lehrer)
                elif stunde.lehrergeändert:
                    lehrerMitUnterricht.add(stunde.lehrer)
                    lehrerVielleichtKrank.add(klasse.kurs(stunde.kursnummer).lehrer)
                elif not stunde.ausfall and not stunde.lehrergeändert:
                    lehrerMitUnterricht.add(stunde.lehrer)

        return sorted(
            {
                lehrer for lehrer in lehrerVielleichtKrank
                if lehrer not in lehrerMitUnterricht
                and lehrer != ""
                and lehrer is not None
            }
        )

    def saveasfile(self, pfad: Path = "./datei.xml", overwrite=False) -> None:
        """Speichert alle Daten des Tages als XML-Datei

        Parameter
        ---------
        pfad : Path
            Der Dateipfad der zu erstellenden Datei
        overwrite : bool
            Ob die Datei überschrieben werden darf, falls sie bereits existiert

        Raises
        --------
        FileExistsError : Falls eine bereits existierende Datei überschrieben werden soll, obwohl `overwrite` `False` ist
        """

        xmlpretty = prettyxml(self._data)

        zielpfad = Path(pfad).resolve()
        zielverzeichnis = zielpfad.parent

        if not zielverzeichnis.exists():
            zielverzeichnis.mkdir(parents=True)

        if zielpfad.exists() and not overwrite:
            raise FileExistsError(f"Die Datei {zielpfad} existiert bereits.")

        zielpfad.write_text(xmlpretty, encoding="utf-8")

    @classmethod
    def fromfile(cls, pfad: Path) -> VertretungsTag:
        """
        Erzeugt ein VpDay-Objekt aus einer XML-Vertretungsplandatei vom Typ K

        Parameter
        ----------
        pfad: Path
            Dateipfad einer XML-Datei vom Typ K

        Raises
        ----------
        FileNotFoundError : Wenn die Datei nicht existiert
        ValueError : Wenn die Datei nicht gelesen werden kann
        """
        with open(pfad) as f:
            vpday = cls(_data=XML.parse(f))
        return vpday


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Klasse                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class Klasse():
    """Klasse, die den Vertretungsplan für eine bestimmte Klasse an einem bestimmten Tag repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: Klasse = vpday.klasse("10a")
    stunden_zur_dritten = data[3]
    ```
    """

    _data: XML.Element

    @property
    def kürzel(self) -> str:
        "Kürzel der Klasse"
        return self._data.find('Kurz').text

    def __repr__(self):
        return f"Vertretungsplan der Klasse {self.kürzel}"
    
    def __getitem__(self, v) -> list[Stunde]:
        return self.stundenHeuteInPeriode(v)

    def stundenHeuteInPeriode(self, periode: int) -> list[Stunde]:
        "Gibt die Stunden der Klasse an dem Tag in einer bestimmten Unterrichtsperiode zurück"
        return self.stundenHeute.get(periode)
    
    @property
    def stundenHeute(self) -> dict[int, list[Stunde]] | None:
        """Alle Stunden der Klasse an dem Tag als Dictionary<br>
        Die Schlüssel sind die Unterrichtsperioden, die Werte Listen von Unterrichsstunden
        """

        fin: dict[int, list[Stunde]] = {}
        pl = self._data.find("Pl")
        for std in pl.findall("Std"):
            stunde = Stunde(std)
            nr = stunde.periode
            if nr is not None:
                if fin.get(stunde.periode) is None:
                    fin[stunde.periode] = [stunde]
                else:
                    fin[stunde.periode].append(stunde)
        return fin
    
    @property
    def kurse(self) -> list[Kurs]:
        "Alle im Plan vermerkten Kurse, die die Klasse hat"
        fin: list[Kurs] = []
        unterricht = self._data.find("Unterricht")
        for ue in unterricht.findall("Ue"):
            fin.append(Kurs(ue.find("UeNr")))
        return fin
    
    def kurs(self, kursnummer: int) -> Kurs | None:
        "Gibt den Kurs mit `kursnummer` der Klasse zurück"
        for kurs in self.kurse:
            if kurs.kursnummer == kursnummer:
                return kurs
        return None

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Stunde                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class Stunde():
    """Klasse, die eine bestimmte Unterrichtsstunde repräsentiert.
    """

    _data: XML.Element
        
    @property
    def periode(self) -> int:
        "Unterrichtsperiode der Stunde"
        return int(self._data.find("St").text)

    @property
    def beginn(self) -> time:
        "Beginn der Stunde"
        return datetime.strptime(self._data.find("Beginn").text, "%H:%M").time()
    
    @property
    def ende(self) -> time:
        "Ende der Stunde"
        return datetime.strptime(self._data.find("Ende").text, "%H:%M").time()
    
    @property
    def ausfall(self) -> bool:
        "Ob die Stunde entfällt"
        return self._data.find("Fa").text == "---"

    @property
    def fach(self) -> str | None:
        """Fach der Stunde<br>
        Gibt `None` zurück, wenn die Stunde entfällt

        Es kann sein, dass nicht das wirkliche Fach sondern die Kursbezeichnung zurückgegeben wird. Stattdessen `klasse.kurs(stunde.kursnummer)` verwenden.<br>
        Bei Unsicherheit mit Fallback: `stunde.fach if klasse.kurs(stunde.kursnummer) is None else klasse.kurs(stunde.kursnummer).fach`
        """
        if self._data.find("Fa") is not None and self._data.find("Fa").text not in [None, "---"]:
            return self._data.find("Fa").text
        else:
            return None
        
    @property
    def lehrer(self) -> str | None:
        """Lehrer der Stunde<br>
        Gibt `None` zurück, wenn die Stunde entfällt
        """
        if self._data.find("Le") is not None and self._data.find("Le").text is not None:
            return self._data.find("Le").text
        else:
            return None

    @property
    def raum(self) -> str | None:
        """Raum der Stunde<br>
        Gibt `None` zurück, wenn die Stunde entfällt
        """
        if self._data.find("Ra") is not None and self._data.find("Ra").text is not None:
            return self._data.find("Ra").text
        else:
            return None
        
    @property
    def fachgeändert(self) -> bool:
        "Ob eine Änderung des Fachs für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "FaAe" in self._data.find("Fa").attrib
    
    @property
    def lehrergeändert(self) -> bool:
        "Ob eine Änderung des Lehrers für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "LeAe" in self._data.find("Le").attrib
    
    @property
    def raumgeändert(self) -> bool:
        "Ob eine Änderung des Raums für die Stunde vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return "RaAe" in self._data.find("Ra").attrib
        
    @property
    def geändert(self) -> bool:
        "Ob eine Änderung im Plan vorliegt<br>Ebenfalls `True`, wenn die Stunde entfällt"
        return self.fachgeändert or self.lehrergeändert or self.raumgeändert

    @property
    def kursnummer(self) -> int | None:
        """Nummer des Kurses der Stunde<br>
        Kann `None` sein, wenn das Fach der Stunde geändert wurde, jedoch nicht, wenn die Stunde entfällt.<br>
        Kann `None` sein, beispielsweise wenn die Stunde eine Exkursion ist.
        
        Kursnummern können verwendet werden, um in den Kursen einer Klasse mehr Details zu einem Kurs zu erhalten, beispielsweise, wenn eine Unterrichtsstunde ausfällt und Informationen wie Lehrer, Fach und Raum deswegen nicht verfügbar sind.<br>
        """
        if self._data.find("Nr") is not None and self._data.find("Nr").text is not None:
            return int(self._data.find("Nr").text)
        else:
            return None
    
    @property
    def info(self) -> str | None:
        "Zusätzliche Information der Stunde"
        if self._data.find("If") is not None and self._data.find("If").text is not None and self._data.find("If").text != "":
            return self._data.find("If").text
        else:
            return None

    def __repr__(self):
        if self.ausfall:
            return f"<Ausfall: '{self.info}'>"
        return f"<'{self.fach}' bei '{self.lehrer}' in Raum '{self.raum}'>"

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Kurs                                             │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class Kurs():
    """Klasse die einen bestimmten Kurs repräsentiert.
    """

    _data: XML.Element

    @property
    def lehrer(self) -> str | None:
        "Lehrer des Kurses"
        if self._data.attrib.get("UeLe") is not None and self._data.attrib.get("UeLe") != "":
            return self._data.attrib["UeLe"]
        else:
            return None
    
    @property
    def fach(self) -> str | None:
        "Fach des Kurses"
        if self._data.attrib.get("UeFa") is not None and self._data.attrib.get("UeFa") != "":
            return self._data.attrib["UeFa"]
        else:
            return None
    
    @property
    def gruppe(self) -> str | None:
        "Gruppenbezeichnung des Kurses"
        if self._data.attrib.get("UeGr") is not None and self._data.attrib.get("UeGr") != "":
            return self._data.attrib["UeGr"]
        else:
            return None

    @property
    def kursnummer(self) -> int:
        "Kursnummer des Kurses"
        return int(self._data.text)

    def __repr__(self) -> str:
        return f"<'{self.fach}' bei '{self.lehrer}', Gruppe '{self.gruppe or '-'}' (Kursnummer '{self.kursnummer}')>"