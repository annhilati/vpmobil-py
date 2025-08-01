from __future__ import annotations
import xml.etree.ElementTree as XML
import os as OS

from datetime import datetime, date, time
from dataclasses import dataclass

from .exceptions import XMLNotFound
from .lib import prettyxml

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         VpDay                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class VpDay():
    """
    Enthält alle Daten für einen bestimmten Tag
    
    #### Attribute
        datum (date): Datum, für das der Plan gilt
        wochentag (int): Wochentag für den der Vertretungsplan gilt
        zusatzInfo (str): Vom Planer eingetragene Zusatzinformation zum Tag
        zeitstempel (datetime): Veröffentlichungszeitpunkt des Vertretungsplans
        datei (str): Dateiname der Quelldatei

    #### Methoden
        klassen(): Liefert eine Liste der im Plan vorhandenen Klassen mitsamt Daten
        klasse(): Isoliert die Daten einer Klasse
        freieTage(): Liefert eine Liste der als frei markierten Tage
        lehrerKrank(): Liefert eine Liste der Lehrer die unplanmäßig keinen Untericht haben
        saveasfile(): Speichert alle Daten des Tages als XML-Datei

    #### Formate
        xml: Gibt die XML-Daten als String zurück
    """

    _data: XML.ElementTree
        
    @property
    def zeitstempel(self) -> datetime:
        "Veröffentlichungszeitpunkt des Vertretungsplans"
        return datetime.strptime(self._data.find('Kopf/zeitstempel').text, "%d.%m.%Y, %H:%M")
        
    @property
    def datei(self) -> str:
        "Dateiname der Quelldatei"
        return self._data.find('Kopf/datei').text

    @property
    def datum(self) -> date:
        "Datum für das der Vertretungsplan gilt"
        return datetime.strptime(self.datei[6:14], "%Y%m%d").date()

    @property
    def zusatzInfo(self) -> str:
        "Vom Planer eingetragene Zusatzinformation zum Tag"
        ziZeilen = []
        for zusatzInfo in self._data.findall('.//ZusatzInfo'):
            for ziZeile in zusatzInfo.findall('.//ZiZeile'):
                if ziZeile.text:
                    ziZeilen.append(ziZeile.text)
        return '\n'.join(ziZeilen)

    def __repr__(self): return f"<Vertretungsplan vom {self.datum.strftime('%d.%m.%Y')}>"

    @property     
    def klassen(self) -> list[Klasse]:
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
        raise XMLNotFound(f"Keine Klassen gefunden")

    def klasse(self, kürzel: str):
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
        raise XMLNotFound(f"Keine Klasse {kürzel} gefunden")

    @property
    def freieTage(self) -> list[date]:
        "Gibt eine Liste der im Plan als frei markierten Tage zurück"

        freieTage = self._data.find("FreieTage")
        if freieTage is None:
            raise XMLNotFound("Element 'FreieTage' nicht in den XML-Daten gefunden")
        
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
                alleStd = Klasse(kl).stunden()
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

    def saveasfile(self, pfad: str = "./datei.xml", overwrite = False) -> None:
        # Es ist noch strittig ob diese Funktion eher zu io gehört
        """
        Speichert alle Daten des Tages als XML-Datei an einen bestimmten Ort
        
        #### Argumente
            pfad (str): Zielpfad der zu erstellenden Datei.
                - Muss den Dateinamen mit Endung enthalten. z.B.: `"./ein/realtiver/ordner/datei.xml"`
            overwrite (bool): Bestimmt, ob die Datei mit dem angegebenen Pfad überschrieben werden soll, wenn sie bereits existiert.
        
        #### Raises
            FileExistsError: Wenn die Datei am Zielpfad entgegen der overwrite-Bestimmung überschrieben werden soll 
        """

        xmlpretty = prettyxml(self._data)

        zielpfad = OS.path.abspath(pfad)
        directory = OS.path.dirname(zielpfad)

        if not OS.path.exists(directory): # Stellt sicher, dass das Verzeichnis existiert
            OS.makedirs(directory)
        if OS.path.exists(zielpfad) and overwrite == False:
            raise FileExistsError(f"Die Datei {zielpfad} existiert bereits.")
        
        with open(zielpfad, "w", encoding="utf-8") as f:
            f.write(xmlpretty)

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Klasse                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class Klasse():
    """
    Enthält alle Daten für eine bestimmte Klasse

    #### Attribute
        kürzel (str): Kürzel der Klasse

    #### Methoden
        stundenInPeriode(): Gibt eine Liste aller Stunden zur angegebenen Stundenplanperiode zurück
        stunden(): Gibt eine Liste aller Stunden der Klasse zurück
    
    #### Formate
        xml: Gibt die XML-Daten als String zurück
    """

    _data: XML.Element

    @property
    def kürzel(self) -> str:
        "Kürzel der Klasse"
        return self._data.find('Kurz').text

    def __repr__(self):
        return f"Vertretungsplan der Klasse {self.kürzel}"

    # def stunde(self, periode: int):
    #     """
    #     Gibt die erste Stunde der angegebenen Stundenplanperiode zurück.\n

    #     #### Argumente:
    #         periode (int): Stundenplanperiode, zur der die Stunde gesucht wird

    #     #### Returns:
    #         Stunde: angefragtes Stunden-Objekt, dass alle Informationen über die Stunde enthält

    #     #### Raises:
    #         XMLNotFound: Wenn die gesuchte Stunde nicht existiert
    #     """

    #     pl = self._data.find("Pl")
    #     for std in pl.findall("Std"):
    #         st = std.find("St")
    #         if st is not None and st.text == str(periode):
    #             return Stunde(std)
    #     raise Exceptions.XMLNotFound("Stunde wurde nicht gefunden!")

    def stundenInPeriode(self, periode: int):
        """
        Gibt eine Liste der Stunden in der angegebenen Stundenplanperiode zurück.\n

        #### Argumente:
            periode (int): Stundenplanperiode, zur der die Stunden gesucht werden

        #### Returns:
            list[Stunde]: Liste von Stunden-Objekten, die alle Informationen über die Stunde enthalten

        #### Raises:
            XMLNotFound: Wenn die gesuchten Stunden nicht existieren
        """

        fin: list[Stunde] = []
        pl = self._data.find("Pl")
        for std in pl.findall("Std"):
            st = std.find("St")
            if st is not None and st.text == str(periode):
                fin.append(Stunde(_data=std))
        if len(fin) != 0:
            return fin
        else:
            raise XMLNotFound("Keine Stunden zu dieser Stundenplanperiode gefunden!")
    
    def stunden(self):
        """
        Gibt alle Stunden des Tages zurück.

        #### Returns:
            list[Stunde]: Liste von Stunden-Objekten in der richtigen Reihenfolge, die alle Informationen über die Stunden enthalten

        #### Raises:
            XMLNotFound: Wenn die gesuchte Stunde nicht existiert
        """

        fin: list[Stunde] = []
        pl = self._data.find("Pl")
        for std in pl.findall("Std"):
            st = std.find("St")
            if st is not None:
                fin.append(Stunde(std))
        if len(fin) != 0:
            return fin
        else:
            raise XMLNotFound("Keine Stunden für diese Klasse gefunden!")
        
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

    def alleKurse(self):
        """
        Gibt eine Liste aller Kurse zurück, die die Klasse am Tag hat.

        #### Returns:
            list[Kurs]: Eine Liste von Kurs-Objekten, die alle Informationen enthalten
        """
        
        fin: list[Kurs] = []
        for i, elem in enumerate(self._data.find("Unterricht").findall("Ue")):
            fin.append(Kurs(elem))
        return fin
    
    
    def alleKurseHeute(self):
        """
        Gibt alle Kurse zurück, welche die Klasse an diesem Tag planmäßig hätte.

        #### Returns:
            list[Kurs]: Eine Liste von Kurs-Objecten, die an diesem Tag planmäßig stattfinden würden
        
        #### Raises:
            XMlNotFound: In besonderen Situationen (z.B. Exkursion) ist manchmal kein Kurs angegeben
        """

        alleKurse: list[Kurs] = self.alleKurse()
        stdHeut: list[Stunde] = self.stunden()
        fin: list[Kurs] = []
        for i, elem in enumerate(stdHeut):
            try:
                fin.append([x for x in alleKurse if x.kursnummer == str(elem.kursnummer)][0])
            except:
                raise XMLNotFound("Keine passenden Kurse gefunden!")
        return fin

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Stunde                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class Stunde():
    """
    Enthält Informationen über eine bestimmte Stunde

    #### Attribute
        nr (int): Stundenplanperiode in der die Stunde stattfindet
        beginn (str): Beginn der Stunde im Schema \"07:45\"
        ende (str): Beginn der Stunde im Schema \"07:45\"
        anders (bool): Gibt an, ob eine Änderung vorliegt
        besonders (bool): Gibt an, ob die Stunde kein normaler Kursuntericht ist
        ausfall (bool): Gibt an, ob die Stunde entfällt
        fach (str): Unterichtsfach der Stunde
        lehrer (str): Lehrer der Stunde
        raum (str): Raum der Stunde
        info (str): Zusätzliche Information zu dieser Stunde
        kursnummer (int): Nummer des Kurses der Stunde

    #### Formate
        xml: Gibt die XML-Daten als String zurück
    """

    _data: XML.Element

    @property
    def nr(self) -> int:
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

    def __repr__(self): return f"Stundenobjekt der {self.nr}. Stunde bei {self.lehrer}"

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Kurs                                             │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

@dataclass
class Kurs():
    """
    Enthält alle Informationen zu einem bestimmten Kurs

    #### Attribute:
        lehrer (str): Der Lehrer, welcher diesen Kurs hält
        fach (str): Das Fach, welches dieser Kurs hat
        zusatz (str): Manche Kurse haben eine Zusatzinformation, wie z.B. Fördern
        kursnummer (int): Die Nummer dieses Kurses.
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
        self.kursnummer: int = self._data.text