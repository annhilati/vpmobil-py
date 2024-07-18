from datetime import datetime, date
import requests as WEB

from .workflow import Exceptions
from .VpDay import VpDay

class Vertretungsplan():
    """
    Enthält die notwendigen Daten um auf einen stundenplan24.de-Vertretungsplan zuzugreifen

    #### Argumente
    - schulnummer (int)
    - benutzername (str)
    - passwort (str)
    - url (str): Pfad des Speicherorts der XML-Quelldateien. Platzhalter:
        - {schulnummer}
    - dateinamensschema (str): z.B `PlanKl%Y%m%d.xml`. Nutze Zeitplatzhalter des datetime-Moduls: 
        - %Y: Jahr (24)
        - %m: Monat (05)
        - %d: Tag (07)

    #### Attribute & Methoden
    - .fetch()
    """

    def __init__(self,
                 schulnummer: int,
                 benutzername: str,
                 passwort: str,
                 url: str = "stundenplan24.de/{schulnummer}/mobil/mobdaten",
                 dateinamensschema: str = "PlanKl%Y%m%d.xml"):
        """
        #### Argumente
        - schulnummer (int)
        - benutzername (str)
        - passwort (str)
        - url (str): Pfad des Speicherorts der XML-Quelldateien. Platzhalter:
            - {schulnummer}
        - dateinamensschema (str): z.B `PlanKl%Y%m%d.xml`. Nutze Zeitplatzhalter des datetime-Moduls: 
            - %Y: Jahr (24)
            - %m: Monat (05)
            - %d: Tag (07)
        """
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort

        if url.endswith('/'):
            url= url[:-1]
        if url.startswith("http://") or url.startswith("https://"):
            parts = url.split("://", 1)
            url = parts[1] if len(parts) > 1 else parts[0]
        self._webpath = f"http://{benutzername}:{passwort}@{url.format(schulnummer=schulnummer)}"
        
        self._dateischema = dateinamensschema

    def fetch(self, datum: date | int = date.today()):
        """
        Ruft alle Daten für einen bestimmten Tag ab und schreibt sie in ein VpDay-Objekt\n
        Ein Error (FetchingError) wird ausgegeben, wenn für den angegebenen Tag keine Daten verfügbar sind.

        - datum: Bestimmter Tag als date-Objekt oder yymmdd-String. Leer lassen, um das heutige Datum abzurufen
        """

        datum: date = datetime.strptime(str(datum), "%Y%m%d").date() if isinstance(datum, int) else datum

        datei: str = datum.strftime(f"{self._dateischema}")
        uri = f"{self._webpath}/{datei}"  
        response = WEB.get(uri)

        if response.status_code != 200:
            raise Exceptions.FetchingError(f"Die Daten für das Datum {datum} konnten nicht abgerufen werden. Statuscode: {response.status_code}", status_code=response.status_code)

        return VpDay(xmldata=response.content)