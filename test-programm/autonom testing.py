import requests
import xml.etree.ElementTree as ET

class Stundenplan():
    """
    Refers to a specific account on a specific VpMobil-Stundenplan
    """

    def __init__(self, schulnummer: int, benutzername: str, passwort: str):
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort
        self.webpath = f"http://{benutzername}:{passwort}@stundenplan24.de/{schulnummer}/mobil/mobdaten/"

    def fetch(self, date: int):
        """
        Creates a VpDay object containing all information about a specific day

        - date: Specific day in yyyymmdd format
        """

        uri = f"{self.webpath}PlanKl{date}.xml"
        response = requests.get(uri)

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data for date {date}. Status code: {response.status_code}")

        return VpDay(xmldata=response.content)

class VpDay():
    """
    Contains all information about a specific day
    """

    def __init__(self, xmldata: ET.ElementTree | bytes | str):
        self.data = xmldata if isinstance(xmldata, ET.ElementTree) else ET.ElementTree(ET.fromstring(xmldata))

    def getxml(self, format: str = "ElementTree"):
        """
        Returns all the information of the day in a certain format

        - format: "str" or "ElementTree"
        """

        match format:
            case "str":
                return ET.tostring(self.data.getroot(), encoding="utf-8", method="xml").decode('utf-8')
            case "ElementTree":
                return self.data
            case _:
                raise ValueError(f"Unsupported type: {format}")
            
    def getclass(self, class_short: str):
        """
        Finds the class element where Kl/Kurz has the value class_short

        - class_short: The short name of the class to find
        """
        root = self.data.getroot()
        for kl in root.findall('.//Kl'):
            kurz = kl.find('Kurz')
            if kurz is not None and kurz.text == class_short:
                return kl
        return None
    
stundenplan = Stundenplan(10126582, "schueler", "s361o97")

print(stundenplan.fetch(20240619).getclass("9a"))