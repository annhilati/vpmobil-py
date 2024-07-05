from .vpDay import VpDay

from datetime import datetime
#Modules shall be imported as a 3-letter code
import requests as REQ 

class Vertretungsplan():
    """
    Enthält die notwendigen Daten um auf einen stundenplan24.de-Vertretungsplan zuzugreifen
    """

    def __init__(self, schulnummer: int, benutzername: str, passwort: str):
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort
        self.webpath = f"http://{benutzername}:{passwort}@stundenplan24.de/{schulnummer}/mobil/mobdaten/"

    def fetch(self, date: int = datetime.today().strftime('%Y%m%d')):
        """
        Ruft alle Daten für einen bestimmten Tag ab und schreibt sie in ein VpDay-Objekt
        Ein Error wird erhoben, wenn für den angegebenen Tag keine Daten verfügbar sind.

        - date: Bestimmter Tag im Format yyyymmdd. Leer lassen, um das heutige Datum abzurufen
        """

        uri = f"{self.webpath}PlanKl{date}.xml"
        response = REQ.get(uri)

        if response.status_code != 200:
            raise ValueError(f"Die Daten für das Datum {date} konnten nicht abgerufen werden. Statuscode: {response.status_code}")

        return VpDay(xmldata=response.content)