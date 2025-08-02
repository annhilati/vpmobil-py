import requests as WEB
import xml.etree.ElementTree as XML
from dataclasses import dataclass

from datetime import datetime, date, timedelta
from yarl import URL

from .exceptions import FetchingError, InvalidCredentialsError, XMLParsingError
from .parser import VpDay

@dataclass
class Vertretungsplan():
    """Klasse, die den Zugang zu einem Indiware Vertretungsplan repräsentiert.

    Parameter
    ----------
    schulnummer : int
        Schulnummer des Vertretungsplans
    benutzername : str
        Benutzername des Benutzers über den zugegriffen werden soll
    passwort : str
        Passwort des Benutzers über den zugegriffen werden soll
    serverdomain : str
        Domain des Servers, der die Vertretungsplandaten bereitstellt<br>
        Muss angegeben werden, wenn der Vertretungsplan selbst gehostet wird
    vezeichnis : str
        Pfad unter dem die Quelldateien abgerufen werden können<br>
        `{schulnummer}` kann als Platzhalter verwendet werden
    dateinamenschema : str
        Schema der Quelldateinamen<br>
        [Platzhalter des datetime-Moduls](https://strftime.org/) können verwendet werden
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
        """Ruft die Daten eines Tages ab.

        Parameter
        ----------
        datum : date
            Abzurufender Tag.
        datei : str (optional)
            Name der abzurufende Datei inklusive Dateipfad (ohne anführenden Schrägstrich)<br>
            Bei Angabe wird der Parameter `datum` ignoriert

        Raises
        ----------
        FetchingError : Wenn für den Tag keine Daten verfügbar sind oder die verwendete Schulnummer nicht registriert ist.
        InvalidCredentialsError : Wenn Benutzername oder Passwort falsch sind.
        XMLParsingError : Falls die Antwort vom Server kein gültiges XML enthält
        """

        file_name: str = datum.strftime(self.dateinamenschema) if datei is None else datei.format(schulnummer=self.schulnummer)
        
        file_uri = self.webpath / file_name
        response = WEB.get(str(file_uri))

        status = response.status_code
        if status == 200:
            try:
                return VpDay(_data=XML.fromstring(response.content))
            except Exception as e:
                raise XMLParsingError(f"Die Daten sind kein gültiges XML ({e})")
        elif status == 401:
            raise InvalidCredentialsError(message=f"Passwort oder Benutzername sind ungültig.", status_code=status)
        elif status == 404:
            raise FetchingError(message=f"Datei '{file_name}' konnte nicht abgerufen werden. Entweder existiert sie nicht, oder die Schulnummer {self.schulnummer} ist nicht registriert.", status_code=status)
        else:
            response.raise_for_status()

    def fetchall(self) -> list[VpDay]:
        """Ruft alle Pläne in einem Zeitraum von 2 Monaten ab.

        Raises
        ----------
        FetchingError : Wenn für den Tag keine Daten verfügbar sind oder die verwendete Schulnummer nicht registriert ist.
        """

        today = datetime.today().date()

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