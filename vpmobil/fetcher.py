from datetime import datetime, date, timedelta
import requests as WEB
import xml.etree.ElementTree as XML
from yarl import URL
from dataclasses import dataclass

from .exceptions import FetchingError, InvalidCredentialsError
from .parser import VpDay

@dataclass
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
    
    schulnummer:        int
    benutzername:       str
    passwort:           str
    serverdomain:       str = 'stundenplan24.de'
    verzeichnis:        str = "/{schulnummer}/mobil/mobdaten"
    dateinamenschema:   str = "PlanKl%Y%m%d.xml"
        
    def __post_init__(self):

        if self.serverdomain.endswith('/'):
            self.serverdomain= self.serverdomain[:-1]

        if self.serverdomain.startswith("http://") or self.serverdomain.startswith("https://"):
            parts = self.serverdomain.split("://", 1)
            self.serverdomain = parts[1] if len(parts) > 1 else parts[0]

        if self.verzeichnis.endswith('/'):
            self.verzeichnis = self.verzeichnis[:-1]
            
        if not self.verzeichnis.startswith("/"):
            self.verzeichnis = "/" + self.verzeichnis

    @property
    def webpath(self) -> URL:
        return URL.build(
            scheme="http",
            user=self.benutzername,
            password=self.passwort,
            host=self.serverdomain,
            path=self.verzeichnis.format(schulnummer=self.schulnummer)
        )

    def __repr__(self):
        return f"<Vertretungsplan {self.benutzername}@{self.schulnummer}>"

    def fetch(self, datum: date = date.today(), datei: str = None) -> VpDay:
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

        file_name: str = datum.strftime(self.dateinamenschema) if datei is None else datei.format(schulnummer=self.schulnummer)
        
        file_uri = self.webpath / file_name
        response = WEB.get(str(file_uri))

        status = response.status_code
        if status == 200:
            return VpDay(_data=XML.fromstring(response.content))
        elif status == 401:
            raise InvalidCredentialsError(message=f"Passwort oder Benutzername sind ungültig.", status_code=status)
        elif status == 404:
            raise FetchingError(message=f"Datei '{file_name}' konnte nicht abgerufen werden. Entweder existiert sie nicht, oder die Schulnummer {self.schulnummer} ist nicht registriert.", status_code=status)
        else:
            response.raise_for_status()

    def fetchall(self) -> list[VpDay]:
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
                except FetchingError:
                    continue
        if pläne == []:
            raise FetchingError("Es konnten in einem zweimonatigen Zeitraum keine Vertretungspläne gefunden werden.")
        else:
            return pläne