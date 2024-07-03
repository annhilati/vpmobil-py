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

    def __init__(self, xml: bytes):
        self.xml = ET.ElementTree(ET.fromstring(xml))

    def getxml(self, format: str = "ElementTree"):
        """
        Returns all the information of the day in a certain format

        - format: "str" or "ElementTree"
        """

        if format == "str":
            return ET.tostring(self.xml.getroot(), encoding="utf-8", method="xml")
        elif format == "ElementTree":
            return self.xml
        else:
            raise ValueError(f"Unsupported type: {format}")