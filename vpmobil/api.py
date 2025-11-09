from yarl import URL
from enum import StrEnum
from datetime import date
from dataclasses import dataclass
import xml.etree.ElementTree as XML
import requests

from vpmobil.models import VertretungsTag, KlassenVertretungsTag, LehrerVertretungsTag, RaumVertretungsTag

class Stundenplan24Pfade(StrEnum):
    """Enumerator mit den Pfaden für Vertretungsplanquelldateien, wie sie auf `stundenplan24.de` verwendet werden.<br>
    
    Pfade enthalten die Platzhalter `{schulnummer}`, `&Y`, `%m` und `%d`.
    """
    Klassen = "{schulnummer}/mobil/mobdaten/Klassen.xml"
    PlanKl  = "{schulnummer}/mobil/mobdaten/PlanKl%Y%m%d.xml"
    Lehrer  = "{schulnummer}/moble/mobdaten/Lehrer.xml"
    PlanLe  = "{schulnummer}/moble/mobdaten/PlanLe%Y%m%d.xml"
    Raeume  = "{schulnummer}/mobra/mobdaten/Raeume.xml"
    PlanRa  = "{schulnummer}/mobra/mobdaten/PlanRa%Y%m%d.xml"

@dataclass
class Vertretungsplan():
    """Klasse, die den Zugang zu einem Indiware Vertretungsplan regelt.

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
        Die Standardpfade von `stundenplan24.de` sind als Attribute von `Stundenplan24Pfade` verfügbar
    """
    
    schulnummer:        int
    benutzername:       str
    passwort:           str
    serverdomain:       str = "stundenplan24.de"
    port:               int = None
    dateipfadschema:    str = Stundenplan24Pfade.PlanKl
    
    def __post_init__(self):

        if self.serverdomain.endswith('/'):
            self.serverdomain = self.serverdomain[:-1]

        if "://" in self.serverdomain:
            self.serverdomain = self.serverdomain.split("://")[-1]
            
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

    def fetch(self, datum: date = date.today(), /, datei: str = None) -> KlassenVertretungsTag | LehrerVertretungsTag | RaumVertretungsTag:
        """Ruft die Daten eines Tages ab.

        Die Methode sollte nur verwendet werden, wenn zu erwarten ist, welcher Typ zurückgegeben wird.<br>
        Verwende dafür Typ-Annotation: `plan: RaumVertretungsTag = vp.fetch()`<br>
        Falls es unklar ist, kann `vpmobil.MobdatenBase` als Protokoll verwendet werden.

        Parameter
        ----------
        datum : date
            Abzurufender Tag
        datei : str
            Pfad (beginnend nach der TLD) der abzurufenden Datei. `datum` kann parallel mit `datei` durch [Platzhalter des datetime-Moduls](https://strftime.org/) verwendet werden.

        Raises
        ----------
        ResourceNotFound : Wenn für den Tag keine Daten verfügbar sind oder die verwendete Schulnummer nicht registriert ist
        Unauthorized : Wenn die Zugangsdaten keinen Zugriff auf die Datei haben
        ValueError : Falls die Antwort vom Server kein gültiges XML enthält
        """

        dateipfad: str = (
            datum
            .strftime(datei or self.dateipfadschema)
            .format(schulnummer=self.schulnummer)
        )
        
        file_url = self.socket / dateipfad
        response = requests.get(str(file_url))

        status = response.status_code
        if status == 401:
            raise Unauthorized(message=f"Zugangsdaten haben keinen Zugriff auf '{dateipfad}'.", response=response)
        elif status == 404:
            raise ResourceNotFound(message=f"Datei '{dateipfad}' existiert nicht.", response=response)
        else:
            response.raise_for_status()
            return VertretungsTag(XML.fromstring(response.content))
        
class IndiwareFetchingError(Exception):
    """Wenn die angeforderten Daten nicht abgerufen werden können."""
    def __init__(self, message: str, response: requests.Response = None):
        self.message = message
        self.response = response

    def __str__(self):
        return f"{self.message} (Status {self.response.status_code})"
    
class ResourceNotFound(IndiwareFetchingError):
    """Wenn die angeforderten Daten nicht existieren
    
    Subklasse von `IndiwareFetchingError`
    """
    ...

class Unauthorized(IndiwareFetchingError):
    """Wenn die Anmeldedaten keinen Zugriff auf die angeforderten Daten haben.
    
    Subklasse von `IndiwareFetchingError`
    """
    ...

