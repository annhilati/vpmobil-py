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
            
    def getclass(self, class_short: str):
        """
        Returns all information about a specific class

        - class_short: Short name of the class to find
        """
        root = self.data.getroot()
        for kl in root.findall('.//Kl'):
            kurz = kl.find('Kurz')
            if kurz is not None and kurz.text == class_short:
                return VpData(data=kl)
            else:
                print(f"No class {class_short} found")
    
class VpData():
    """
    Contains specific information about a specific day
    Can be built from an XML-Element or -ElementTree
    """
    def __init__(self, data: ET.Element | VpDay):
        self.data = data if isinstance(data, ET.Element) else data.data.getroot()

    def getxml(self, format: str = "Element"):
        """
        Returns all the information of the day in a certain format

        - format: "str" or "Element"
        """

        match format:
            case "str":
                return ET.tostring(self.data, encoding="utf-8", method="xml").decode('utf-8')
            case "Element":
                return self.data
            case _:
                raise ValueError(f"Unsupported type: {format}")