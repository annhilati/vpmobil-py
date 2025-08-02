from __future__ import annotations
import xml.etree.ElementTree as XML
import re

from pathlib import Path
from datetime import datetime, date, time
from dataclasses import dataclass

from .lib import prettyxml

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         VpDay                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class VpDay():
    """Klasse die den Vertretungsplan an einem bestimmten Tag repräsentiert.
    
    Unterstützt Subskription: 
    ```
    data: VpDay = vp.fetch()
    klasse = data["10a"]
    ```
    """

    _data: XML.ElementTree

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
        "Vom Planer eingetragene Zusatzinformationen zum Tag"
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
                kurz = kl.find('Kurz')
                if kurz is not None:
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
        """Liste der Lehrer, die außerplanmäßig keinen Untericht halten<br>
        Dies umfasst auch Lehrer, die schulische Veranstaltung beaufischtigen und deren Stunden deswegen als ausgefallen markiert wurden.
        """

        leKrank: list[str] = []
        leNichtKrank: list[str] = []

        for kl in self._data.find('Klassen').findall("Kl"):
            lehrerInfo: list[dict] = []
            for ue in kl.find("Unterricht").findall("Ue"): # Wir sammeln für alle Kurse dieser Klasse die Nummer und das Lehrerkürzel
                lehrerInfo.append({
                    "nr": ue.find("UeNr").text, 
                    "kurz": ue.find("UeNr").attrib["UeLe"]
                })
            try:
                alleStd = Klasse(kl).stundenHeute
            except:
                continue
            else:
                for st in alleStd: # Jetzt gehen wir durch alle Stunden und schauen, ob sie geändert sind
                    for std in alleStd[st]:
                        if not std.anders and not std.ausfall and not std.besonders: # Wenn nicht fügen wir die Lehrer, welche die Stunde halten zu den nicht kranken Lehrern hinzu
                            for sr in std.lehrer.split(" "):
                                leNichtKrank.append(sr)
                                if sr in leKrank:
                                    leKrank.remove(sr) # Wenn der Lehrer fälschlicherweise als krank eingeordnet wurde, löschen wir ihn aus der kranken Liste
                        elif std.anders and not std.ausfall and not std.besonders:
                            for sr in std.lehrer.split(" "):
                                leNichtKrank.append(sr)
                                if sr in leKrank:
                                    leKrank.remove(sr) # Wenn der Lehrer fälschlicherweise als krank eingeordnet wurde, löschen wir ihn aus der kranken Liste
                        elif std.anders and std.ausfall and not std.besonders:
                            le = next(item for item in lehrerInfo if item["nr"] == str(std.kursnummer))
                            if not (le["kurz"] in leNichtKrank): # Wenn die Stunde geändert ist schauen wir, ob der lehrer schon in der nicht kranken Liste ist.
                                if not le["kurz"] in leKrank:
                                    leKrank.append(le["kurz"]) # Wenn nicht, muss er krank sein
                        elif std.besonders:
                            try:
                                splitLe = std.lehrer.split(" ")
                            except TypeError:
                                continue
                            else:
                                for sr in splitLe:
                                    leNichtKrank.append(splitLe)
        return sorted(leKrank) # Sorry für den mess, aber es funktioniert und fast alles ist leider auch nötig

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
        Die Schlüssel sind die Unterrichtsperioden, die Werte Listen von Unterrichsstunden"""

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

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Stunde                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class Stunde():
    "Klasse, die eine bestimmte Unterrichtsstunde repräsentiert."

    _data: XML.Element

    @property
    def periode(self) -> int | None:
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
    def anders(self) -> bool:
        "Ob eine Änderung im Plan vorliegt"
        return "FaAe" in self._data.find("Fa").attrib or "RaAe" in self._data.find("Ra").attrib or "LeAe" in self._data.find("Le").attrib

    @property
    def ausfall(self) -> bool:
        "Ob die Stunde entfällt"
        return self._data.find("Fa").text == "---"
    
    @property
    def kursnummer(self) -> int:
        """Nummer des Kurses der Stunde<br>
        Kursnummern können verwendet werden, um in den Kursen einer Klasse mehr Details zu einem Kurs zu erhalten, beispielsweise, wenn eine Unterrichtsstunde ausfällt und Informationen wie Lehrer, Fach und Raum deswegen nicht verfügbar sind.<br>
        Ist `-1`, wenn die Stunde nicht Teil eines Kurses ist
        """
        try:
            return int(self._data.find("Nr").text) 
        except:
            return -1

    @property
    def besonders(self) -> bool:
        """
        Gibt an, ob die Stunde besonders ist. (Z.B. True, wenn es sich um eine Exkursion handelt.)\n
        Besondere Stunden haben keine Kursnummer! Prüfe immer erst, ob eine Stunde besonders ist, bevor du die Kursnummer abrufst. .kursnummer gibt dann -1 zurück, wenn die Stunde besonders ist.\n
        Wenn trotzdem ein Lehrer, Fach oder Raum eingetragen ist, wird dieser normal zurückgegeben
        """
        try:
            kursnummer: int = int(self._data.find("Nr").text) 
            return False
        except:
            return True

    @property
    def fach(self) -> str | None:
        """Fach der Stunde<br>
        Gibt einen leeren String zurück, wenn die Stunde entfällt<br>
        Kann auch `None` zurückgeben
        """

        if self._data.find("Fa") is not None and self._data.find("Fa").text is not None:
            fach = self._data.find("Fa").text
        else:
            fach = None
        return fach
        
    @property
    def lehrer(self) -> str | None:
        """Lehrer der Stunde<br>
        Gibt einen leeren String zurück, wenn die Stunde entfällt<br>
        Kann auch `None` zurückgeben
        """
        if self._data.find("Le") is not None and self._data.find("Le").text is not None:
            tmpLe = self._data.find("Le").text
        else:
            tmpLe = None
        return tmpLe

    @property
    def raum(self) -> str | None:
        """Raum der Stunde<br>
        Gibt einen leeren String zurück, wenn die Stunde entfällt<br>
        Kann auch `None` zurückgeben
        """
        if self._data.find("Ra") is not None and self._data.find("Ra").text is not None:
            tmpRa = self._data.find("Ra").text
        else:
            tmpRa = None
        return tmpRa
    
    @property
    def info(self) -> str | None:
        """
        Zusätzliche Information zu dieser Stunde\n
        Ist nur in besonderen Situationen und bei entfallen der Stunde vorhanden
        """
        return self._data.find("If").text

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
    def lehrer(self) -> str:
        "Lehrer des Kurses"
        return self._data.attrib["UeLe"]
    
    @property
    def fach(self) -> str:
        "Fach des Kurses"
        return self._data.attrib["UeFa"]
    
    @property
    def gruppe(self) -> str | None:
        "Gruppenbezeichnung des Kurses"
        return self._data.attrib.get("UeGr")

    @property
    def kursnummer(self) -> int:
        "Kursnummer des Kurses"
        return self._data.text

    def __repr__(self) -> str:
        return f"<'{self.fach}' bei '{self.lehrer}', Gruppe '{self.gruppe or '-'}' (Kursnummer '{self.kursnummer}')>"