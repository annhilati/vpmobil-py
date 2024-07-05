from datetime import datetime, date
#Modules shall be imported as a 3-letter code
import xml.etree.ElementTree as XML 
import requests as REQ 

# ╭────────────────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Vertretungsplan                                            │ 
# ╰────────────────────────────────────────────────────────────────────────────────────────────────────╯

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

        - date: Bestimmter Tag im yyyymmdd-Format oder date-Objekt. Leer lassen, um das heutige Datum abzurufen
        """

        date = date if isinstance(date, int) else date.strftime('%Y%m%d')
        uri = f"{self.webpath}PlanKl{date}.xml"  
        response = REQ.get(uri)

        if response.status_code != 200:
            raise ValueError(f"Die Daten für das Datum {date} konnten nicht abgerufen werden. Statuscode: {response.status_code}")

        return VpDay(xmldata=response.content)
    
# ╭────────────────────────────────────────────────────────────────────────────────────────────────────╮
# │                                              VpDay                                                 │ 
# ╰────────────────────────────────────────────────────────────────────────────────────────────────────╯

class VpDay():
    """
    Enthält alle Daten für einen bestimmten Tag 
    """

    def __init__(self, xmldata: XML.ElementTree | bytes | str):
        self.datatree: XML.ElementTree = xmldata if isinstance(xmldata, XML.ElementTree) else XML.ElementTree(XML.fromstring(xmldata))

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
                raise ValueError(f"Nicht unterstütztes Format: {format}")

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
        vpMobil = self.datatree.getroot()
        freieTageElement = vpMobil.find("FreieTage")
        if freieTageElement is None:
            raise ValueError("Element 'FreieTage' nicht in den XML-Daten gefunden")
        
        freieTage: list[date] = []
        for ft in freieTageElement.findall("ft"):
            if ft.text is not None:
                freieTage.append(datetime.strptime(ft.text, "%y%m%d").date())
        return freieTage
            
    def klasse(self, class_short: str) -> XML.Element:
        """
        Gibt das XML-Element der angegebenen Klasse zurück.
        Ein Fehler wird ausgegeben, wenn die angegebene Klasse nicht gefunden werden kann. 

        - class_short: Kürzel der zu suchenden Klasse (z.B. "8b")
        """
        vpmobil = self.datatree.getroot()
        for kl in vpmobil.findall('.//Kl'):
            kurz = kl.find('Kurz')
            if kurz is not None and kurz.text == class_short:
                return kl
        raise ValueError(f"Keine Klasse {class_short} gefunden")
        