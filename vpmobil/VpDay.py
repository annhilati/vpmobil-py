from datetime import datetime, date
import xml.etree.ElementTree as XML
import xml.dom.minidom
import os as OS

from .workflow import Exceptions

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         VpDay                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VpDay():
    """
    Enthält alle Daten für einen bestimmten Tag
    
    #### Attribute & Methoden
    - .datum
    - .zusatzInfo
    - .zeitstempel
    - .datei
    - .getxml()
    - .klasse()
    - .freieTage()
    - .lehrerKrank()
    """

    def __init__(self, xmldata: XML.ElementTree | bytes | str, datum: date):
        self.datatree: XML.ElementTree = xmldata if isinstance(xmldata, XML.ElementTree) else XML.ElementTree(XML.fromstring(xmldata))
        self.rootVpMobil: XML.Element = self.datatree.getroot()
        self.zeitstempel: datetime = datetime.strptime(self.datatree.find('Kopf/zeitstempel').text, "%d.%m.%Y, %H:%M")
        "Zeitpunkt, zu dem der Vertretungsplan veröffentlicht wurde"
        self.datei: str = self.datatree.find('Kopf/datei').text
        "Dateiname der XML-Quelldatei"
        self.datum = datum
        "Datum für das der Vertretungsplan gilt"

        ziZeilen = []
        for zusatzInfo in self.rootVpMobil.findall('.//ZusatzInfo'):
            for ziZeile in zusatzInfo.findall('.//ZiZeile'):
                if ziZeile.text:
                    ziZeilen.append(ziZeile.text)
        self.zusatzInfo = '\n'.join(ziZeilen)
        "Gibt die Zusatzinformationen des Tages zurück"

    def __format__(self, format):
        match format:
            case "str": return XML.tostring(self.datatree.getroot(), encoding="utf-8", method="xml").decode('utf-8')
            case "ElementTree": return self.datatree
            case _: raise SyntaxError(f"Nicht unterstütztes Format: {format}")
            
    def saveasfile(self, pfad: str = "./", allowoverwrite = False):
        """
        Speichert alle Daten des Tages als XML-Datei an einen bestimmten Ort
        
        #### Argumente
        - pfad: Zielpfad der zu erstellenden Datei. Muss den Dateinamen mit Endung enthalten
        - allowoverwrite: Bestimmt, ob die Datei mit dem angegebenen Pfad überschrieben werden soll, wenn sie bereits existiert.
        Gibt einen Fehler (FileExistsError) aus, wenn eine Datei entgegen dieser Angabe überschrieben werden soll 
        #### Beispiele
        - `.saveasfile("./datei.xml")`
        - `.saveasfile(f"./{.datum}")`
        """
        string = XML.tostring(self.rootVpMobil, 'utf-8')
        pretty = xml.dom.minidom.parseString(string).toprettyxml(indent="\t")

        zielpfad = OS.path.abspath(pfad)
        directory = OS.path.dirname(zielpfad)

        if not OS.path.exists(directory): # Stellt sicher, dass das Verzeichnis existiert
            OS.makedirs(directory)
        if OS.path.exists(zielpfad) and allowoverwrite == False:
            raise FileExistsError(f"Die Datei {zielpfad} existiert bereits.")
        
        with open(zielpfad, "w", encoding="utf-8") as f:
            f.write(pretty)
            
    def klasse(self, kürzel: str):
        """
        Gibt ein Klassen-Objekt zurück, dass alle Daten über die Klasse enthält\n
        Ein Fehler (XMLNotFound) wird ausgegeben, wenn die angegebene Klasse nicht gefunden werden kann. 

        - kürzel: Kürzel der zu suchenden Klasse (z.B. "8b")
        """

        for kl in self.rootVpMobil.findall('.//Kl'):
            kurz = kl.find('Kurz')
            if kurz is not None and kurz.text == kürzel:
                return Klasse(xmldata=kl)
        raise Exceptions.XMLNotFound(f"Keine Klasse {kürzel} gefunden")

    def freieTage(self) -> list[date]:
        "Gibt eine Liste der im Plan als frei markierten Tage zurück"

        freieTage = self.rootVpMobil.find("FreieTage")
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

        for kl in self.rootVpMobil.find('Klassen').findall("Kl"):
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

    #### Attribute & Methoden
    - .getxml()
    - .stunde()
    - .stundenInPeriode()
    - .alleStunden()
    """

    def __init__(self, xmldata: XML.Element):
        self.data: XML.Element = xmldata

    def __format__(self, format):
        match format:
            case "str": return XML.tostring(self.data(), encoding="utf-8", method="xml").decode('utf-8')
            case "Element": return self.data
            case _: raise SyntaxError(f"Nicht unterstütztes Format: {format}")

    def stunde(self, periode: int): # macht diese Funktion Sinn? Wer braucht denn random nur den ersten Kurs?
        """
        Gibt die erste Stunde der angegebenen Stundenplanperiode zurück.\n
        Ein Fehler (XMLNotFound) wird ausgegeben, wenn die gesuchte Stunde nicht existiert
        """

        pl = self.data.find("Pl")
        for std in pl.findall("Std"):
            st = std.find("St")
            if st is not None and st.text == str(periode):
                return Stunde(std)
        raise Exceptions.XMLNotFound("Stunde wurde nicht gefunden!")

    def stundenInPeriode(self, periode: int):
        """
        Gibt alle Stunden zurück, die in der angegebenen Stundenplanperiode stattfinden.\n
        Ein Fehler (XMLNotFound) wird ausgegeben, wenn die gesuchten Stunden nicht existieren
        """

        fin: list[Stunde] = []
        pl = self.data.find("Pl")
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
        Gibt alle Stunden zurück, die die Klasse an diesem Tag hat.
        Ein Fehler (XMLNotFound) wird ausgegeben, wenn keine Stunden existieren
        """

        fin: list[Stunde] = []
        pl = self.data.find("Pl")
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

    #### Attribute & Methoden
    - .nr
    - .beginn
    - .ende
    - .anders
    - .ausfall
    - .fach
    - .lehrer
    - .raum
    - .info
    - .kursnummer
    """

    def __init__(self, xmldata: XML.Element | bytes | str):
        self.data: XML.Element = xmldata if isinstance(xmldata, XML.Element) else XML.Element(XML.fromstring(xmldata))
        self.nr: int = int(self.data.find("St").text)
        "Nummer der Stunde"

        self.beginn: str = str(self.data.find("Beginn").text)
        "Beginn der Stunde im Format \"07:45\""

        self.ende: str = str(self.data.find("Ende").text)
        "Ende der Stunde im Format \"08:30\""

        if "FaAe" in self.data.find("Fa").attrib or "RaAe" in self.data.find("Ra").attrib or "LeAe" in self.data.find("Le").attrib:
            anders = True
        else:
            anders = False
        self.anders: bool = anders
        "Gibt an, ob eine Änderung vorliegt"

        if self.data.find("Fa").text == "---":
            ausfall = True
        else:
            ausfall = False
        self.ausfall: bool = ausfall
        """
        Gibt an, ob die Stunde entfällt\n
        Wenn ja, werden 'lehrer', 'fach' und 'raum' leere Strings zurückgeben
        """

        self.besonders: bool = False
        """
        Gibt an, ob die Stunde besonders ist. Gibt True zurück, wenn es sich z.B. um eine Exkursion handelt.\n
        Achtung: Besondere Stunden haben keine Kursnummer! Prüfe immer erst, ob eine Stunde besonders ist, bevor du die Kursnummer abrufst.\n
        .kursnummer gibt -1 zurück, wenn die Stunde besonders ist.\n
        Wenn trotzdem ein Lehrer, Fach oder Raum eingetragen ist, wird dieser normal zurückgegeben
        """
        try:
            kursnummer: int = int(self.data.find("Nr").text) 
        except:
            self.besonders = True
            kursnummer: int = -1
        self.kursnummer: int = kursnummer
        """
        Nummer des Kurses der Stunde, Nützlich für das Kurs() Objekt\n
        Ist -1, wenn die Stunde nicht Teil eines Kurses ist
        """

        if self.data.find("Fa") is not None and self.data.find("Fa").text is not None:
            tmpFa = self.data.find("Fa").text
        else:
            tmpFa = ""
        self.fach: str = tmpFa if self.ausfall == False and self.besonders == False else ""
        """
        Unterichtsfach der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """
        
        if self.data.find("Le") is not None and self.data.find("Le").text is not None:
            tmpLe = self.data.find("Le").text
        else:
            tmpLe = ""
        self.lehrer: str = tmpLe if self.ausfall == False else ""
        """
        Lehrer der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """

        if self.data.find("Ra") is not None and self.data.find("Ra").text is not None:
            tmpRa = self.data.find("Ra").text
        else:
            tmpRa = ""
        self.raum: str = tmpRa if self.ausfall == False else ""
        """
        Raum der Stunde\n
        Gibt einen leeren String zurück, wenn die Stunde entfällt oder besonders ist
        """

        self.info: str = self.data.find("If").text
        """
        Optionale Information zu dieser Stunde\n
        Ist nur in besonderen Situationen und bei entfallen der Stunde vorhanden
        """
