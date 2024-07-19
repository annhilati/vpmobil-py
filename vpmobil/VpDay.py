import xml.dom.minidom
import xml.etree.ElementTree as XML
import os as OS
from datetime import datetime, date

from .workflow import Exceptions

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         VpDay                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VpDay():
    """
    Enthält alle Daten für einen bestimmten Tag
    
    #### Attribute
        datum (date): Datum, für das der Plan gilt
        zusatzInfo (str): Vom Planer eingetragene Zusatzinformation zum Tag
        zeitstempel (datetime): Veröffentlichungszeitpunkt des Vertretungsplans
        datei (str): Dateiname der Quelldatei

    #### Methoden
        klasse(): Isoliert die Daten einer Klasse
        freieTage(): Liefert eine Liste der als frei markierten Tage
        lehrerKrank(): Liefert eine Liste der Lehrer die unplanmäßig keinen Untericht haben
        saveasfile(): Speichert alle Daten des Tages als XML-Datei

    #### Formate
        xml: Gibt die XML-Daten als String zurück
    """

    def __init__(self, xmldata: XML.ElementTree | bytes | str):
        self._datatree: XML.ElementTree = xmldata if isinstance(xmldata, XML.ElementTree) else XML.ElementTree(XML.fromstring(xmldata))
        self._dataroot: XML.Element = self._datatree.getroot()
        
        self.zeitstempel: datetime = datetime.strptime(self._datatree.find('Kopf/zeitstempel').text, "%d.%m.%Y, %H:%M")
        "Veröffentlichungszeitpunkt des Vertretungsplans"
        
        self.datei: str = self._datatree.find('Kopf/datei').text
        "Dateiname der Quelldatei"
        
        self.datum = datetime.strptime(self.datei[6:14], "%Y%m%d").date()
        "Datum für das der Vertretungsplan gilt"

        ziZeilen = []
        for zusatzInfo in self._dataroot.findall('.//ZusatzInfo'):
            for ziZeile in zusatzInfo.findall('.//ZiZeile'):
                if ziZeile.text:
                    ziZeilen.append(ziZeile.text)
        self.zusatzInfo = '\n'.join(ziZeilen)
        "Vom Planer eingetragene Zusatzinformation zum Tag"

    def __format__(self, format_spec):
        match format_spec:
            case "xml": return XML.tostring(self._datatree.getroot(), encoding="utf-8", method="xml").decode('utf-8')
            case _: raise SyntaxError(f"Unbekanntes Format: {format_spec}")
            
    def saveasfile(self, pfad: str = "./datei.xml", overwrite = False) -> None:
        """
        Speichert alle Daten des Tages als XML-Datei an einen bestimmten Ort
        
        #### Argumente
            pfad (str): Zielpfad der zu erstellenden Datei.
                Muss den Dateinamen mit Endung enthalten. z.B.: `"./ein/realtiver/ordner/datei.xml"`
            overwrite (bool): Bestimmt, ob die Datei mit dem angegebenen Pfad überschrieben werden soll, wenn sie bereits existiert.
        
        #### Raises
            FileExistsError: Wenn die Datei am Zielpfad entgegen der overwrite-Bestimmung überschrieben werden soll 
        """

        xmlstring = XML.tostring(self._dataroot, 'utf-8')
        xmlpretty = xml.dom.minidom.parseString(xmlstring).toprettyxml(indent="\t")

        zielpfad = OS.path.abspath(pfad)
        directory = OS.path.dirname(zielpfad)

        if not OS.path.exists(directory): # Stellt sicher, dass das Verzeichnis existiert
            OS.makedirs(directory)
        if OS.path.exists(zielpfad) and overwrite == False:
            raise FileExistsError(f"Die Datei {zielpfad} existiert bereits.")
        
        with open(zielpfad, "w", encoding="utf-8") as f:
            f.write(xmlpretty)
            
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

        for kl in self._dataroot.findall('.//Kl'):
            kurz = kl.find('Kurz')
            if kurz is not None and kurz.text == kürzel:
                return Klasse(xmldata=kl)
        raise Exceptions.XMLNotFound(f"Keine Klasse {kürzel} gefunden")

    def freieTage(self) -> list[date]:
        "Gibt eine Liste der im Plan als frei markierten Tage zurück"

        freieTage = self._dataroot.find("FreieTage")
        if freieTage is None:
            raise Exceptions.XMLNotFound("Element 'FreieTage' nicht in den XML-Daten gefunden")
        
        freieTageList: list[date] = []
        for ft in freieTage.findall("ft"):
            if ft.text is not None:
                freieTageList.append(datetime.strptime(ft.text, "%y%m%d").date())
        return freieTageList
    
    def lehrerKrank(self) -> list[str]:
        """
        Gibt eine Liste mit den Kürzeln aller Lehrer zurück, die außerplanmäßig keinen Untericht halten.\n
        Dies umfasst auch Lehrer, die schulische Veranstaltung beaufischtigen, zu denen Stunden vom Planer als ausgefallen markiert wurden.
        """

        leKrank: list[str] = []
        leNichtKrank: list[str] = []

        for kl in self._dataroot.find('Klassen').findall("Kl"):
            lehrerInfo: list[dict] = []
            for ue in kl.find("Unterricht").findall("Ue"): # Wir sammeln für alle Kurse dieser Klasse die Nummer und das Lehrerkürzel
                lehrerInfo.append({
                    "nr": ue.find("UeNr").text, 
                    "kurz": ue.find("UeNr").attrib["UeLe"]
                })
            try:
                alleStd = Klasse(kl).alleStunden()
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


# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Klasse                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Klasse():
    """
    Enthält alle Daten für eine bestimmte Klasse

    #### Methoden
        stunde(): Gibt die erste Stunde zur angegebenen Stundenplanperiode
        stundenInPeriode(): Gibt eine Liste aller Stunden zur angegebenen Stundenplanperiode zurück
        alleStunden(): Gibt eine Liste aller Stunden der Klasse zurück
    
    #### Formate
        xml: Gibt die XML-Daten als String zurück
    """

    def __init__(self, xmldata: XML.Element):
        self._data: XML.Element = xmldata

    def __format__(self, format_spec):
        match format_spec:
            case "xml": return XML.tostring(self._data, encoding="utf-8", method="xml").decode('utf-8')
            case _: raise SyntaxError(f"Unbekanntes Format: {format_spec}")

    def stunde(self, periode: int): # macht diese Funktion Sinn? Wer braucht denn random nur den ersten Kurs?
        """
        Gibt die erste Stunde der angegebenen Stundenplanperiode zurück.\n

        #### Argumente:
            periode (int): Stundenplanperiode, zur der die Stunde gesucht wird

        #### Returns:
            Stunde: angefragtes Stunden-Objekt, dass alle Informationen über die Stunde enthält

        #### Raises:
            XMLNotFound: Wenn die gesuchte Stunde nicht existiert
        """

        pl = self._data.find("Pl")
        for std in pl.findall("Std"):
            st = std.find("St")
            if st is not None and st.text == str(periode):
                return Stunde(std)
        raise Exceptions.XMLNotFound("Stunde wurde nicht gefunden!")

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
                fin.append(Stunde(xmldata=std))
        if len(fin) != 0:
            return fin
        else:
            raise Exceptions.XMLNotFound("Keine Stunden zu dieser Stundenplanperiode gefunden!")
    
    def alleStunden(self):
        """
        Gibt alle Stunden des Tages zurück.\n

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
            raise Exceptions.XMLNotFound("Keine Stunden für diese Klasse gefunden!")

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Stunde                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

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

    def __init__(self, xmldata: XML.Element | bytes | str):
        self._data: XML.Element = xmldata if isinstance(xmldata, XML.Element) else XML.Element(XML.fromstring(xmldata))
        
        self.nr: int = int(self._data.find("St").text)
        "Stundenplanperiode in der die Stunde stattfindet"

        self.beginn: str = str(self._data.find("Beginn").text)
        "Beginn der Stunde im Schema \"07:45\""

        self.ende: str = str(self._data.find("Ende").text)
        "Ende der Stunde im Schema \"08:30\""

        if "FaAe" in self._data.find("Fa").attrib or "RaAe" in self._data.find("Ra").attrib or "LeAe" in self._data.find("Le").attrib:
            anders = True
        else:
            anders = False
        self.anders: bool = anders
        "Gibt an, ob eine Änderung vorliegt"

        if self._data.find("Fa").text == "---":
            ausfall = True
        else:
            ausfall = False
        self.ausfall: bool = ausfall
        """
        Gibt an, ob die Stunde entfällt\n
        Wenn ja, geben '.lehrer', '.fach' und '.raum' leere Strings zurück
        """

        self.besonders: bool = False
        """
        Gibt an, ob die Stunde besonders ist. (Z.B. True, wenn es sich um eine Exkursion handelt.)\n
        Besondere Stunden haben keine Kursnummer! Prüfe immer erst, ob eine Stunde besonders ist, bevor du die Kursnummer abrufst. .kursnummer gibt dann -1 zurück, wenn die Stunde besonders ist.\n
        Wenn trotzdem ein Lehrer, Fach oder Raum eingetragen ist, wird dieser normal zurückgegeben
        """
        try:
            kursnummer: int = int(self._data.find("Nr").text) 
        except:
            self.besonders = True
            kursnummer: int = -1
        self.kursnummer: int = kursnummer
        """
        Nummer des Kurses der Stunde, Nützlich für das Kurs() Objekt\n
        Ist -1, wenn die Stunde nicht Teil eines Kurses ist
        """

        if self._data.find("Fa") is not None and self._data.find("Fa").text is not None:
            fach = self._data.find("Fa").text
        else:
            fach = ""
        self.fach: str = fach if self.ausfall == False and self.besonders == False else ""
        """
        Unterichtsfach der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """
        
        if self._data.find("Le") is not None and self._data.find("Le").text is not None:
            tmpLe = self._data.find("Le").text
        else:
            tmpLe = ""
        self.lehrer: str = tmpLe if self.ausfall == False else ""
        """
        Lehrer der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """

        if self._data.find("Ra") is not None and self._data.find("Ra").text is not None:
            tmpRa = self._data.find("Ra").text
        else:
            tmpRa = ""
        self.raum: str = tmpRa if self.ausfall == False else ""
        """
        Raum der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """

        self.info: str = self._data.find("If").text
        """
        Zusätzliche Information zu dieser Stunde\n
        Ist nur in besonderen Situationen und bei entfallen der Stunde vorhanden
        """

    def __format__(self, format_spec):
        match format_spec:
            case "xml": return XML.tostring(self._data, encoding="utf-8", method="xml").decode('utf-8')
            case _: raise SyntaxError(f"Unbekanntes Format: {format_spec}")

def getxml(object: VpDay | Klasse | Stunde) -> XML.ElementTree | XML.Element:
    # Der Docstring befindet sich in __init__.py

    if isinstance(object, VpDay): return object._datatree
    elif isinstance(object, Klasse): return object._data
    elif isinstance(object, Stunde): return object._data
    else: raise TypeError("object muss einer der Typen VpDay, Klasse & Stunde sein") # Der Code ist ereichbar lol habs getestet