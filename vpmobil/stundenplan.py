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
        Creates a vpDay object containing all information about a specific day

        - date: Specific day in yyyymmdd format
        """

        uri = f"{self.webpath}PlanKl{date}.xml"
        response = requests.get(uri)

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data for date {date}. Status code: {response.status_code}")

        return vpDay(xml=response.content)

class vpDay():
    """
    Contains all information about a specific day
    """

    # def __init__(self, xml: bytes):
    #     self.data = ET.ElementTree(ET.fromstring(xml))
    def __init__(self, xml: str | ET.ElementTree):
        self.data = ET.ElementTree(ET.fromstring(xml)) if isinstance(xml, str) else xml

    def getxml(self, format: str = "ElementTree"):
        """
        Returns all the information of the day in a certain format

        - format: "str" or "ElementTree"
        """

        match format:
            case "str":
                return ET.tostring(self.data.getroot(), encoding="utf-8", method="xml")
            case "ElementTree":
                return self.data
            case _:
                raise ValueError(f"Unsupported type: {format}")