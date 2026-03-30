from yarl import URL
from enum import StrEnum
from datetime import date, timedelta
from dataclasses import dataclass
import xml.etree.ElementTree as XML
import requests

from vpmobil.models import VertretungsTag, KlassenVertretungsTag, LehrerVertretungsTag, RaumVertretungsTag

class Stundenplan24Pfade(StrEnum):
    """Enumerator mit den Pfaden für Vertretungsplanquelldateien, wie sie auf `stundenplan24.de` verwendet werden.<br>
    
    Pfade enthalten die Platzhalter `{schulnummer}`, `%%Y`, `%%m` und `%%d`.
    """
    Klassen = "{schulnummer}/mobil/mobdaten/Klassen.xml"
    PlanKl  = "{schulnummer}/mobil/mobdaten/PlanKl%Y%m%d.xml"
    Lehrer  = "{schulnummer}/moble/mobdaten/Lehrer.xml"
    PlanLe  = "{schulnummer}/moble/mobdaten/PlanLe%Y%m%d.xml"
    Raeume  = "{schulnummer}/mobra/mobdaten/Raeume.xml"
    PlanRa  = "{schulnummer}/mobra/mobdaten/PlanRa%Y%m%d.xml"

@dataclass
class Vertretungsplan():
    """Das Vertretungsplan-Objekt verwaltet den Zugang und das Abrufen von
    Daten über Zugangsdaten zu einem Indiware-Vertretungsplan. Pro Instanz
    werden standardmäßig nur Vertretungspläne eines Typs abgerufen.
    Beliebige andere Dateien können aber dennoch durch Angabe des
    Dateipfads abgerufen werden.

    Üblicherweise ist stark begrenzt, welche Planart für einen Benutzer
    verfügbar ist. Schüler-Benutzer können deswegen nur Klassenpläne abrufen.
    Lehrer- und Raumpläne können allerdings unter gewissen Verlusten aus den
    Klassenplänen rekonstruiert werden. Funktionen dafür sind in
    `vpmobil.extensions.reparser` verfügbar.

    Parameters:
        schulnummer (int): Schulnummer der Schule auf deren Plan zugegriffen werden soll
        benutzername (str): Benutzername des Benutzers über den zugegriffen werden soll
        passwort (str): Passwort des Benutzers über den zugegriffen werden soll
        domain (str): Domain des Servers, der die Vertretungsplandaten bereitstellt
        port (int): Port des Service, der die Vertretungsplandaten bereitstellt
        dateipfadschema (str):
            Schema der Pfade unter dem die Quelldateien abgerufen werden können.
            `{schulnummer}` sowie strftime-Direktiven können als Platzhalter verwendet werden.
            Die Standardpfade sind im Enumerator `Stundenplan24Pfade` enthalten.
    """
    
    schulnummer:      int
    benutzername:     str
    passwort:         str
    serverdomain:     str = "stundenplan24.de"
    port:             int = None
    dateipfadschema:  str = Stundenplan24Pfade.PlanKl
    
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

        Parameters:
            datum (date): Datum des abzurufenden Tags
            datei (str): Pfad der abzurufenden Datei (beginnend nach der Domain). Wenn
                sowohl `datum` als auch `datei` angegeben sind, wird das Datum aus `datum`
                in `datei` eingesetzt, falls letzteres strftime-Direktiven enthält.

        Raises:
            ResourceNotFound: Wenn für den Tag keine Daten verfügbar sind oder die
                verwendete Schulnummer nicht registriert ist
            Unauthorized: Wenn die Zugangsdaten keinen Zugriff auf die Datei haben

        Für beide Fehler gibt es verschiedene mögliche Ursachen, die in den
        entsprechenden Fehlerklassen genauer beschrieben sind.
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
            raise Unauthorized(message=f"Zugangsdaten haben keinen Zugriff auf '{dateipfad}'", response=response)
        elif status == 404:
            raise ResourceNotFound(message=f"Datei '{dateipfad}' existiert nicht", response=response)
        else:
            response.raise_for_status()
            return VertretungsTag(XML.fromstring(response.content))
        
    def bulkfetch(self, standardplan: str = Stundenplan24Pfade.Klassen, try_weekend: bool = False) -> list[KlassenVertretungsTag | LehrerVertretungsTag | RaumVertretungsTag]:

        standard = self.fetch(datei=standardplan)

        results: list[VertretungsTag] = []

        for tag in (tag for tag in (date.today() + timedelta(days=i) for i in range(-14, 15))
                    if (try_weekend or tag.weekday() < 5) and tag not in standard.freieTage):
            try:
               results.append(self.fetch(tag))
            except VpMobilPyError:
                continue

        return results
        
        
class VpMobilPyError(Exception):
    """Angeforderte Daten können nicht abgerufen werden. Mögliche Ursachen für
    bestimmte Fehler sind in den entsprechenden Subklassen genauer beschrieben.
    """
    def __init__(self, message: str, response: requests.Response = None):
        self.message = message
        self.response = response

    def __str__(self):
        return self.message
    
class ResourceNotFound(VpMobilPyError):
    """Angeforderte Daten existieren nicht. (Subklasse von `VpMobilPyError`)

    Für diesen Fehler typische Ursachen sind:
    - Die Schulnummer ist nicht registriert 
    - Der angeforderte Tag ist nicht (mehr) verfügbar. In der Regel stehen nur Pläne für
        die Tage von bis zu zwei Wochen um den aktuellen Tag zum Abrufen zur Verfügung.
    - Die Schule verwendet eine eigene Instanz von VpMobil. In diesem Fall ist es
        notwendig herauszufinden, unter welcher Domain und ggf. unter welchem Pfad die
        Quelldateien bereitgestellt werden. Hierfür kann Hilfe im
        [Bugtracker von vpmobil-py](https://github.com/annhilati/vpmobil-py/issues) in
        Anspruch genommen werden.
    - Die Schule stellt Pläne der angeforderten Art nicht zur Verfügung.
    """
    ...

class Unauthorized(VpMobilPyError):
    """Anmeldedaten haben keinen Zugriff auf die angeforderten Daten. (Subklasse von `VpMobilPyError`)

    Für diesen Fehler typische Ursachen sind:
    - Benutzername oder Passwort sind ungültig.
    - Der Benutzer hat keine Berechtigung, um auf Pläne der angeforderten Art zuzugreifen.
    """
    ...