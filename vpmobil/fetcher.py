from datetime import datetime, date, timedelta
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
        fetch(): Ruft die Daten eines Tages oder einer Datei ab
        fetchall(): Ruft alle Tage in einem 2 monatigem Zeitraum ab
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

        if verzeichnis.endswith('/'):
            serverurl = serverurl[:-1]
        if verzeichnis.startswith("/"):
            serverurl = serverurl[1:]

        self._webpath = f"{benutzername}:{passwort}@{serverurl}/{verzeichnis.format(schulnummer=schulnummer)}"
        self._dateinamenschema = dateinamenschema

    def __repr__(self): return f"Vertretungsplan {self.benutzername}@{self.schulnummer}"

    def fetch(self, datum: date | int = date.today(), datei: str = None):
        """
        Ruft die Daten eines Tages oder einer Datei ab

        #### Argumente:
            datum (date | int): Abzurufender Tag.
                int muss im Schema yyyymmdd sein (z.B. `20240609`)
            datei (str): Abzurufende Datei mit Dateipfad.
                z.B. `"{schulnummer}/mobil/mobdaten/Klassen.xml"`. Ignoriert datum bei Angabe

        #### Returns:
            VpDay: Die angeforderten Daten

        #### Raises:
            FetchingError: Wenn für den Tag keine Daten verfügbar sind oder die verwendete Schulnummer nicht registriert ist.
            InvalidCredentialsError: Wenn Benutzername oder Passwort falsch sind.
        """

        datum: date = datetime.strptime(str(datum), "%Y%m%d").date() if isinstance(datum, int) else datum

        file: str = datum.strftime(self._dateinamenschema) if datei is None else datei.format(schulnummer=self.schulnummer)
        
        uri = f"http://{self._webpath}/{file}"
        response = WEB.get(uri)

        http = response.status_code
        if http == 200:
            return VpDay(mobdaten=response.content)
        elif http == 401:
            raise Exceptions.InvalidCredentialsError(message=f"Passwort oder Benutzername sind ungültig.", status_code=http)
        elif http == 404:
            raise Exceptions.FetchingError(message=f"Datei {datei} konnte nicht abgerufen werden. Entweder existiert sie nicht, oder die Schulnummer {self.schulnummer} ist nicht registriert.", status_code=http)
        else:
            response.raise_for_status()

    def fetchall(self):
        """
        Gibt alle Pläne in einem Zeitraum von 2 Monaten als Liste zurück

        #### Returns
            list[VpDay]: Die Liste an angeforderten Plänen
        
        #### Raises
            FetchingError: Wenn keine Pläne gefunden werden konnten
        """
        #raise NotImplementedError
        today = datetime.today().date()#.strftime("%Y%m%d")

        def date_range(start_date: date, end_date: date):
            delta = timedelta(days=1)
            current_date = start_date
            while current_date <= end_date:
                yield current_date
                current_date += delta

        pläne: list[VpDay] = []
        for tag in date_range(today - timedelta(days=30), today + timedelta(days=30)):
            if tag.weekday() > 4:
                continue
            else:
                try:
                    plan = self.fetch(tag)
                    pläne.append(plan)
                except Exceptions.FetchingError:
                    continue
        if pläne == []:
            raise Exceptions.FetchingError("Es konnten in einem zweimonatigen")
        else:
            return pläne