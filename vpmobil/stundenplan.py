import requests
import xml.etree.ElementTree as ET
from datetime import datetime

class Stundenplan():
    """
    Contains the necessary data to access a stundenplan24.de substitution plan
    """

    def __init__(self, schulnummer: int, benutzername: str, passwort: str):
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort
        self.webpath = f"http://{benutzername}:{passwort}@stundenplan24.de/{schulnummer}/mobil/mobdaten/"

    def fetch(self, date: int = datetime.today().strftime('%Y%m%d')):
        """
        Retrieves all data for a specific day and writes it to a VpDay object.
        An error is raised if no data is available for the specified day

        - date: Specific day in yyyymmdd format. Leave empty to retrieve today's date
        """

        uri = f"{self.webpath}PlanKl{date}.xml"
        response = requests.get(uri)

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data for date {date}. Status code: {response.status_code}")

        return VpDay(xmldata=response.content)

class VpDay():
    """
    Contains all data for a specific day 
    """

    def __init__(self, xmldata: ET.ElementTree | bytes | str):
        self.datatree: ET.ElementTree = xmldata if isinstance(xmldata, ET.ElementTree) else ET.ElementTree(ET.fromstring(xmldata))

    def getxml(self, format: str = "ElementTree") -> (ET.ElementTree | str):
        """
        Returns all data for the day in a specific format

        - format: "str" or "Element"
        """
        
        match format:
            case "str":
                return ET.tostring(self.datatree.getroot(), encoding="utf-8", method="xml").decode('utf-8')
            case "ElementTree":
                return self.datatree
            case _:
                raise ValueError(f"Unsupported type: {format}")
            
    def get_substitution(self, class_short):
        # """
        # Returns a list of the substitution planned for a class

        # - class_short: Short name of the class to find
        # """
        # vpmobil = self.data.getroot()
        # for kl in vpmobil.findall('.//Kl'):
        #     kurz = kl.find('Kurz')
        #     if kurz is not None and kurz.text == class_short:
        #         return kl
        #     else:
        #         print(f"No class {class_short} found")
        pass