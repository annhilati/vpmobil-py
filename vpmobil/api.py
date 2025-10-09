from yarl import URL
from dataclasses import dataclass
from datetime import datetime, date, timedelta
import xml.etree.ElementTree as XML
import requests

from vpmobil.models import VertretungsTagBase, VertretungsTag, LehrerVertretungsTag, RaumVertretungsTag

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
        Domain des Servers, der die Vertretungsplandaten bereitstellt
    port : int
        Port des Service, der die Vertretungsplandaten bereitstellt
    dateipfadschema : str
        Schema des Pfads unter dem die Quelldateien abgerufen werden können<br>
        `{schulnummer}` kann als Platzhalter verwendet werden<br>
        [Platzhalter des datetime-Moduls](https://strftime.org/) können verwendet werden<br>
        Die Standardpfade von `stundenplan24.de` sind als Attribute von `vpmobil.utils.Stundenplan24Pfade` verfügbar
    """
    
    schulnummer:        int
    benutzername:       str
    passwort:           str
    serverdomain:       str = "stundenplan24.de"
    port:               int = None
    dateipfadschema:    str = "{schulnummer}/mobil/mobdaten/PlanKl%Y%m%d.xml"
    
    def __post_init__(self):

        if self.serverdomain.endswith('/'):
            self.serverdomain = self.serverdomain[:-1]

        if "://" in self.serverdomain:
            self.serverdomain = self.serverdomain.split("://", 1)[-1]
            
        if self.dateipfadschema.startswith("/"):
            self.dateipfadschema = self.dateipfadschema[1:]

    @property
    def socket(self) -> URL:
        return URL.build(
            scheme="http",
            user=self.benutzername,
            password=self.passwort,
            host=self.serverdomain,
            port=self.port
        )

    def __repr__(self):
        return f"<Vertretungsplan {self.benutzername}@{self.schulnummer}>"

    def fetch(self, datum: date = date.today(), datei: str = None) -> VertretungsTag | LehrerVertretungsTag | RaumVertretungsTag:
        """Ruft die Daten eines Tages ab.

        Parameter
        ----------
        datum : date
            Abzurufender Tag
        datei : str
            Pfad (beginnend nach der TLD) der abzurufenden Datei. `datum` kann parallel mit `datei` durch [Platzhalter des datetime-Moduls](https://strftime.org/) verwendet werden.

        Raises
        ----------
        ResourceNotFound : Wenn für den Tag keine Daten verfügbar sind oder die verwendete Schulnummer nicht registriert ist
        InvalidCredentialsError : Wenn Benutzername oder Passwort falsch sind
        ValueError : Falls die Antwort vom Server kein gültiges XML enthält
        """

        dateipfad: str = (
            datum
            .strftime(self.dateipfadschema if datei is None else datei)
            .format(schulnummer=self.schulnummer)
        ) 
        
        file_url = self.socket / dateipfad
        response = requests.get(str(file_url))

        status = response.status_code
        if status == 200:
            return VertretungsTagBase(XML.fromstring(response.content))
        elif status == 401:
            raise InvalidCredentialsError(message=f"Passwort oder Benutzername sind ungültig.", response=response)
        elif status == 404:
            raise ResourceNotFound(message=f"Datei '{dateipfad}' konnte nicht abgerufen werden. Entweder existiert sie nicht, oder die Schulnummer '{self.schulnummer}' ist nicht registriert.", response=response)
        else:
            response.raise_for_status()

    def bulkfetch(self) -> list[VertretungsTag | LehrerVertretungsTag | RaumVertretungsTag]:
        """Ruft alle Pläne in einem Zeitraum von 2 Monaten ab.

        Raises
        ----------
        ResourceNotFound : Wenn keine Daten verfügbar sind oder die verwendete Schulnummer nicht registriert ist.
        InvalidCredentialsError : Wenn Benutzername oder Passwort falsch sind.
        ValueError : Falls eine Antwort vom Server kein gültiges XML enthält
        """

        today = datetime.today().date()

        def date_range(start_date: date, end_date: date):
            delta = timedelta(days=1)
            current_date = start_date
            while current_date <= end_date:
                yield current_date
                current_date += delta

        pläne: list[VertretungsTagBase] = []
        for tag in date_range(today - timedelta(days=30), today + timedelta(days=30)):
            if tag.weekday() > 4:
                continue
            else:
                try:
                    plan = self.fetch(tag)
                    pläne.append(plan)
                except IndiwareFetchingError:
                    continue
        if len(pläne) == 0:
            raise ResourceNotFound("Es konnten in einem zweimonatigen Zeitraum keine Vertretungspläne gefunden werden.")
        else:
            return pläne
        
class IndiwareFetchingError(Exception):
    "Wenn die angeforderten Daten nicht abgerufen werden können"
    def __init__(self, message: str, response: requests.Response = None):
        self.message = message
        self.response = response

    def __str__(self):
        return f"{self.message} ({self.response})"
    
class ResourceNotFound(IndiwareFetchingError):
    "Wenn die angeforderten Daten nicht existieren"
    ...

class InvalidCredentialsError(IndiwareFetchingError):
    "Wenn die Anmeldedaten ungültig sind"
    ...