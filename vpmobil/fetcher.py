from datetime import datetime, date
import requests as WEB

from .exceptions import Exceptions
from .parser import VpDay

class Vertretungsplan():
    """
    Enthält die notwendigen Daten um auf einen stundenplan24.de-Vertretungsplan zuzugreifen

    #### Argumente:
        schulnummer (int): Schulnummer des Vertretungsplans
        benutzer (str): Benutzername des Benutzers über den zugegriffen werden soll
        passwort (str): Passwort des Benutzers über den zugegriffen werden soll
        serverurl (str): URL und Verzeichnispfad
            - Muss angegeben werden, wenn der Vertretungsplan selbst gehostet wird
        vezeichnis (str): Pfad an dem die Quelldateien gespeichert werden
            - z.B. `'{schulnummer}/mobil/mobdaten'`. Es kann `{schulnummer}` als Platzhalter verwendet werden
        dateinamenschema (str): Schema der Quelldateinamen
            - z.B. `'PlanKl%Y%m%d.xml'`. Es können [Platzhalter des datetime-Moduls](https://strftime.org/) verwendet werden

    #### Methoden:
        fetch(): Ruft die Daten eines Tages ab
    """

    def __init__(self,
                 schulnummer: int,
                 benutzername: str,
                 passwort: str,
                 serverurl: str = 'stundenplan24.de',
                 verzeichnis: str = "{schulnummer}/mobil/mobdaten",
                 dateinamenschema: str = "PlanKl%Y%m%d.xml"):
        """
        #### Argumente:
            schulnummer (int): Schulnummer des Vertretungsplans
            benutzer (str): Benutzername des Benutzers über den zugegriffen werden soll
            passwort (str): Passwort des Benutzers über den zugegriffen werden soll
            serverurl (str): URL und Verzeichnispfad
                - Muss angegeben werden, wenn der Vertretungsplan selbst gehostet wird
            vezeichnis (str): Pfad an dem die Quelldateien gespeichert werden
                - z.B. `"{schulnummer}/mobil/mobdaten"`. Es kann `{schulnummer}` als Platzhalter verwendet werden
            dateinamenschema (str): Schema der Quelldateinamen
                - z.B. `"PlanKl%Y%m%d.xml"`. Es können [Platzhalter des datetime-Moduls](https://strftime.org/) verwendet werden
        """
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort

        if serverurl.endswith('/'):
            serverurl= serverurl[:-1]
        if serverurl.startswith("http://") or serverurl.startswith("https://"):
            parts = serverurl.split("://", 1)
            serverurl = parts[1] if len(parts) > 1 else parts[0]

        if verzeichnis.startswith('/'):
            serverurl = serverurl[:-1]
        if verzeichnis.startswith("/"):
            serverurl = serverurl[1:]

        self._webpath = f"{benutzername}:{passwort}@{serverurl}/{verzeichnis.format(schulnummer=schulnummer)}"
        self._dateinamenschema = dateinamenschema

    def __repr__(self): return f"Vertretungsplan {self.benutzername}@{self.schulnummer}"

    def fetch(self, datum: date | int = date.today(), datei: str = None):
        """
        Ruft die Daten eines Tages ab

        #### Argumente:
            datum (date | int): Abzurufender Tag
                int muss im Schema yyyymmdd sein (z.B. `20240609`)
            datei (str): Abzurufende Datei mit Dateipfad
                z.B. `"{schulnummer}/mobil/mobdaten/Klassen.xml"`. Ignoriert datum bei Angabe

        #### Raises:
            FetchingError: Wenn für den Tag keine Daten verfügbar sind
        """

        datum: date = datetime.strptime(str(datum), "%Y%m%d").date() if isinstance(datum, int) else datum

        datei: str = datum.strftime(self._dateinamenschema) if datei is None else datei.format(schulnummer=self.schulnummer)
        
        uri = f"http://{self._webpath}/{datei}"
        response = WEB.get(uri)

        if response.status_code != 200:
            if datei is not None:
                errormsg = f"Die Datei {datei} konnten nicht abgerufen werden. Statuscode: {response.status_code}"
            else: 
                errormsg = f"Die Daten für das Datum {datum} konnten nicht abgerufen werden. Statuscode: {response.status_code}"

            raise Exceptions.FetchingError(message=errormsg, status_code=response.status_code)

        return VpDay(mobdaten=response.content)