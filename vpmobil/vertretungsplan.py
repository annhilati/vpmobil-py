from datetime import datetime, date
#Modules shall be imported as a 3-letter code
import xml.etree.ElementTree as XML 
import requests as WEB

from .Exceptions import FetchingError, XMLError

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    Vertretungsplan                                       │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Vertretungsplan():
    """
    Enthält die notwendigen Daten um auf einen stundenplan24.de-Vertretungsplan zuzugreifen
    """

    def __init__(self, schulnummer: int, benutzername: str, passwort: str):
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort
        self.webpath = f"http://{benutzername}:{passwort}@stundenplan24.de/{schulnummer}/mobil/mobdaten/"

    def fetch(self, date: int | date = datetime.today().date()):
        """
        Ruft alle Daten für einen bestimmten Tag ab und schreibt sie in ein VpDay-Objekt
        Ein Error wird erhoben, wenn für den angegebenen Tag keine Daten verfügbar sind.

        - date: Bestimmter Tag; Integer im yyyymmdd-Format oder date-Objekt. Leer lassen, um das heutige Datum abzurufen
        """

        date = date if isinstance(date, int) else date.strftime('%Y%m%d')
        uri = f"{self.webpath}PlanKl{date}.xml"  
        response = WEB.get(uri)

        if response.status_code != 200:
            raise FetchingError(f"Die Daten für das Datum {date} konnten nicht abgerufen werden. Statuscode: {response.status_code}")

        return VpDay(xmldata=response.content)
    
# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         VpDay                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VpDay():
    """
    Enthält alle Daten für einen bestimmten Tag 
    """

    def __init__(self, xmldata: XML.ElementTree | bytes | str):
        self.datatree: XML.ElementTree = xmldata if isinstance(xmldata, XML.ElementTree) else XML.ElementTree(XML.fromstring(xmldata))
        self.rootVpMobil: XML.Element = self.datatree.getroot()

    def getxml(self, format: str = "ElementTree") -> (XML.ElementTree | str):
        """
        Gibt alle Daten für den Tag in einem bestimmten Format zurück

        - format: Das Format, in dem die Daten ausgegeben werden sollen. Eines von "str" oder "ElementTree".
        """

        match format:
            case "str":
                return XML.tostring(self.datatree.getroot(), encoding="utf-8", method="xml").decode('utf-8')
            case "ElementTree":
                return self.datatree
            case _:
                raise SyntaxError(f"Nicht unterstütztes Format: {format}")
            
    def klasse(self, class_short: str) -> XML.Element:
        """
        Gibt das XML-Element der angegebenen Klasse zurück.
        Ein Fehler wird ausgegeben, wenn die angegebene Klasse nicht gefunden werden kann. 

        - class_short: Kürzel der zu suchenden Klasse (z.B. "8b")
        """

        for kl in self.rootVpMobil.findall('.//Kl'):
            kurz = kl.find('Kurz')
            if kurz is not None and kurz.text == class_short:
                return kl
        raise XMLError(f"Keine Klasse {class_short} gefunden")
        

    def zeitstempel(self) -> datetime:
        """
        Gibt den Zeitpunkt zurück, zu dem der Vertretungsplan veröffentlicht wurde
        """

        zeitstempel = self.datatree.find('Kopf/zeitstempel').text
        return datetime.strptime(zeitstempel, "%d.%m.%Y, %H:%M")
    
    def zusatzInfo(self) -> str:
        """
        Gibt die Zusatzinformationen des Tages zurück
        """

        return self.datatree.find("ZusatzInfo/ZiZeile").text

    def freieTage(self) -> list[date]:
        """
        Gibt eine Liste der im Plan als frei markierten Tage zurück
        """

        freieTage = self.rootVpMobil.find("FreieTage")
        if freieTage is None:
            raise XMLError("Element 'FreieTage' nicht in den XML-Daten gefunden")
        
        freieTageList: list[date] = []
        for ft in freieTage.findall("ft"):
            if ft.text is not None:
                freieTageList.append(datetime.strptime(ft.text, "%y%m%d").date())
        return freieTageList

class Stunde():
    """
    Enthält Informationen über eine bestimmte Stunde
    """

    def __init__(self, elem: XML.Element | bytes | str):
        self.std = elem if isinstance(elem, XML.Element) else XML.Element(XML.fromstring(elem))
        self.nr : int = int(self.std.find("St").text)
        """
        Nummer der Stunde
        """

        self.beginn : str = str(self.std.find("Beginn").text)
        """
        Beginn der Stunde als str()
        """

        self.ende : str = str(self.std.find("Ende").text)
        """
        Ende der Stunde als str()
        """

        if "FaAe" in self.std.find("Fa").attrib or "RaAe" in self.std.find("Ra").attrib or "LeAe" in self.std.find("Le").attrib:
            anders = True
        else:
            anders = False
        self.anders : bool = anders
        """
        Gibt an, ob irgendeine Eigenschaft dieser Stunde geändert ist
        """

        if self.std.find("Fa").text == "---":
            ausfall = True
        else:
            ausfall = False
        self.entfaellt : bool = ausfall
        """
        Gibt an, ob die Stunde entfällt. 
        Wenn ja, werden 'lehrer', 'fach' und 'raum' leere Strings zurückgeben
        """

        self.fach : str = self.std.find("Fa").text if self.entfaellt == False else ""
        """
        Gibt das Fach, welches in dieser Stunde stattfindet zurück.
        Gibt einen leeren String zurück, wenn die Stunde entfällt
        """

        self.lehrer : str = self.std.find("Le").text if self.entfaellt == False else ""
        """
        Gibt den Lehrer, welcher diese Stunde hält zurück.
        Gibt einen leeren String zurück, wenn die Stunde entfällt
        """

        self.raum : str = self.std.find("Ra").text if self.entfaellt == False else ""
        """
        Gibt den Raum, in dem diese Stunde stattfindet zurück.
        Gibt einen leeren String zurück, wenn die Stunde entfällt
        """

        self.kursnummer : str = self.std.find("Nr").text
        """
        Gibt die Nummer des Kurses zurück.
        Nützlich für das Kurs() Objekt
        """

        self.info : str = self.std.find("If").text
        """
        Gibt eine optionale vom Planer verfasste Information zu dieser Stunde.
        Ist nur in besonderen Situationen und bei entfallen der Stunde vorhanden
        """
