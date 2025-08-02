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
        "Vom Planer eingetragene Zusatzinformation zum Tag"
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
        """
        Liefert eine Liste der im Plan vorhandenen Klassen mitsamt Daten

        #### Returns
            list[Klasse]: Liste an Klassenobjekten, die die XML-Daten der Klassen enthalten

        #### Raises
            XMLNotFound: Wenn keine Klassen gefunden werden können
        """
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
        """
        Isoliert die Daten einer Klasse
        
        #### Argumente:
            kürzel (str): Kürzel der zu suchenden Klasse (z.B. `"8b"`)

        #### Returns
            Klasse: Klassenobjekt, dass die XML-Daten der Klasse enthält

        #### Raises
            XMLNotFound: Wenn die angegebene Klasse nicht gefunden werden kann. 
        """

        klassen = self.klassen
        for kl in klassen:
            if kl.kürzel == kürzel:
                return kl
        return None

    @property
    def freieTage(self) -> list[date] | None:
        "Gibt eine Liste der im Plan als frei markierten Tage zurück"

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
        """
        Gibt eine Liste mit den Kürzeln aller Lehrer zurück, die außerplanmäßig keinen Untericht halten.\n
        Dies umfasst auch Lehrer, die schulische Veranstaltung beaufischtigen, zu denen Stunden vom Planer als ausgefallen markiert wurden.
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
                for std in alleStd: # Jetzt gehen wir durch alle Stunden und schauen, ob sie geändert sind
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
        """
        Speichert alle Daten des Tages als XML-Datei an einen bestimmten Ort

        #### Argumente
            pfad (str): Zielpfad der zu erstellenden Datei.
                - Muss den Dateinamen mit Endung enthalten. z.B.: `"./ein/relativer/ordner/datei.xml"`
            overwrite (bool): Bestimmt, ob die Datei mit dem angegebenen Pfad überschrieben werden soll, wenn sie bereits existiert.

        #### Raises
            FileExistsError: Wenn die Datei am Zielpfad entgegen der overwrite-Bestimmung überschrieben werden soll 
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
        """
        """

        return self.stundenHeute.get(periode)
    
    @property
    def stundenHeute(self) -> dict[int, list[Stunde]] | None:
        "Gibt alle Stunden des Tages zurück."

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
        fin: list[Kurs] = []
        unterricht = self._data.find("Unterricht")
        for ue in unterricht.findall("Ue"):
            fin.append(Kurs(ue.find("UeNr")))
        return fin

        
    # def kurseInPeriode(self, periode: int):
    #     """
    #     Gibt alle Kurse zurück, welche in dieser Periode planmäßig stattfinden würden\n
    #     Bei besonderen Stunden (z.B. Exkursion an diesem Tag) kann es zu Fehlern kommen

    #     #### Returns:
    #         list[Kurs]: Eine Liste von Kurs-Objecten, die in dieser Periode planmäßig stattfinden würden
        
    #     #### Raises:
    #         XMLNotFound: Wenn wegen einer besonderen Situation (z.B. Exkursion) kein passender Kurs gefunden werden konnte
    #     """

    #     stdList = self.stundenInPeriode(periode)
    #     fin: list[Kurs] = []
    #     alleKurse: list[Kurs] = []
    #     for i, elemn in enumerate(self._data.find("Unterricht").findall("Ue")):
    #         alleKurse.append(Kurs(elemn))
    #     for i, elem in enumerate(stdList):
    #         try:
    #             fin.append(list(filter(lambda x: x.kursnummer == str(elem.kursnummer), alleKurse))[0])
    #         except:
    #             raise XMLNotFound("Keinen passenden Kurs gefunden!")
    #     return fin

    # def alleKurse(self):
    #     """
    #     Gibt eine Liste aller Kurse zurück, die die Klasse am Tag hat.

    #     #### Returns:
    #         list[Kurs]: Eine Liste von Kurs-Objekten, die alle Informationen enthalten
    #     """
        
    #     fin: list[Kurs] = []
    #     for i, elem in enumerate(self._data.find("Unterricht").findall("Ue")):
    #         fin.append(Kurs(elem))
    #     return fin
    
    
    # def alleKurseHeute(self) -> list[Kurs] | None:
    #     """
    #     Gibt alle Kurse zurück, welche die Klasse an diesem Tag planmäßig hätte.

    #     #### Returns:
    #         list[Kurs]: Eine Liste von Kurs-Objecten, die an diesem Tag planmäßig stattfinden würden
        
    #     #### Raises:
    #         XMlNotFound: In besonderen Situationen (z.B. Exkursion) ist manchmal kein Kurs angegeben
    #     """

    #     alleKurse: list[Kurs] = self.alleKurse()
    #     stdHeut: list[Stunde] = self.stunden()
    #     fin: list[Kurs] = []
    #     for i, elem in enumerate(stdHeut):
    #         try:
    #             fin.append([x for x in alleKurse if x.kursnummer == str(elem.kursnummer)][0])
    #         except:
    #             return None
    #     return fin

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Stunde                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class Stunde():
    "Klasse, die eine bestimmte Unterrichtsstunde repräsentiert."

    _data: XML.Element

    @property
    def periode(self) -> int | None:
        "Stundenplanperiode in der die Stunde stattfindet"
        return int(self._data.find("St").text)

    @property
    def beginn(self) -> time:
        return datetime.strptime(self._data.find("Beginn").text, "%H:%M").time()
    
    @property
    def ende(self) -> time:
        return datetime.strptime(self._data.find("Ende").text, "%H:%M").time()

    @property
    def anders(self) -> bool:
        "Gibt an, ob eine Änderung vorliegt"
        return "FaAe" in self._data.find("Fa").attrib or "RaAe" in self._data.find("Ra").attrib or "LeAe" in self._data.find("Le").attrib

    @property
    def ausfall(self) -> bool:
        """
        Gibt an, ob die Stunde entfällt\n
        Wenn ja, geben '.lehrer', '.fach' und '.raum' leere Strings zurück
        """
        return self._data.find("Fa").text == "---"
    
    @property
    def kursnummer(self) -> int:
        """
        Nummer des Kurses der Stunde, Nützlich für das Kurs() Objekt\n
        Ist -1, wenn die Stunde nicht Teil eines Kurses ist
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
    def fach(self) -> str:
        """
        Unterichtsfach der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """

        if self._data.find("Fa") is not None and self._data.find("Fa").text is not None:
            fach = self._data.find("Fa").text
        else:
            fach = ""
        return fach if self.ausfall == False and self.besonders == False else ""
        
    @property
    def lehrer(self) -> str:
        """
        Lehrer der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """
        if self._data.find("Le") is not None and self._data.find("Le").text is not None:
            tmpLe = self._data.find("Le").text
        else:
            tmpLe = ""
        return tmpLe if self.ausfall == False else ""

    @property
    def raum(self) -> str:
        """
        Raum der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """
        if self._data.find("Ra") is not None and self._data.find("Ra").text is not None:
            tmpRa = self._data.find("Ra").text
        else:
            tmpRa = ""
        return tmpRa if self.ausfall == False else ""
    
    @property
    def info(self) -> str:
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
    def gruppe(self) -> str:
        """
        Zusatzfach des Kurses.\n
        Gibt einen leeren String zurück, wenn es kein Zusatzfach gibt
        """
        return self._data.attrib.get("UeGr", "")

    @property
    def kursnummer(self) -> int:
        "Kursnummer des Kurses"
        return self._data.text

    def __repr__(self) -> str:
        return f"<'{self.fach}' bei '{self.lehrer}', Gruppe '{self.gruppe or '-'}' (Kursnummer '{self.kursnummer}')>"