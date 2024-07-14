from datetime import datetime, date
import requests as WEB

from .workflow import Exceptions
from .VpDay import VpDay

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                    Vertretungsplan                                       │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Vertretungsplan():
    """
    Enthält die notwendigen Daten um auf einen stundenplan24.de-Vertretungsplan zuzugreifen

    #### Argumente
    - schulnummer (int)
    - benutzername (str)
    - passwort (str)

    #### Attribute & Methoden
    - .fetch()
    """

    def __init__(self, schulnummer: int, benutzername: str, passwort: str):
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort
        self.webpath = f"http://{benutzername}:{passwort}@stundenplan24.de/{schulnummer}/mobil/mobdaten/"

    def fetch(self, date: int | date = datetime.today().date()):
        """
        Ruft alle Daten für einen bestimmten Tag ab und schreibt sie in ein VpDay-Objekt\n
        Ein Error (FetchingError) wird ausgegeben, wenn für den angegebenen Tag keine Daten verfügbar sind.

        - date: Bestimmter Tag; Integer im yyyymmdd-Format oder date-Objekt. Leer lassen, um das heutige Datum abzurufen
        """

        date = date if isinstance(date, int) else date.strftime('%Y%m%d')
        uri = f"{self.webpath}PlanKl{date}.xml"  
        response = WEB.get(uri)

        if response.status_code != 200:
            raise Exceptions.FetchingError(f"Die Daten für das Datum {date} konnten nicht abgerufen werden. Statuscode: {response.status_code}", status_code=response.status_code)

        return VpDay(xmldata=response.content)