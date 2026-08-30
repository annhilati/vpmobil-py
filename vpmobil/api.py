from yarl import URL
from enum import StrEnum
from datetime import datetime, date, time, timedelta
from typing import overload
from dataclasses import dataclass, field
import xml.etree.ElementTree as XML
import requests
import configparser

from vpmobil.models import Vertretungsplan
from vpmobil.parser import Parser

class Standardpfade(StrEnum):
    """Enumerator mit den Pfaden für Vertretungsplanquelldateien,
    wie sie auf `stundenplan24.de` verwendet werden. `Klassen`, `Lehrer`
    und `Raeume` enthalten immer die Tage des Plans, der zuletzt
    veröffentlicht wurden. `PlanKl`, `PlanLe` und `PlanRa` enthalten die
    Pläne für beliebige Tage.
    
    Die Pfade enthalten immer den Platzhalter `{schulnummer}`, gegebenenfalls
    auch die strptime-Direktiven `%Y`, `%m` und `%d`.
    """
    Klassen = "{schulnummer}/mobil/mobdaten/Klassen.xml"
    PlanKl  = "{schulnummer}/mobil/mobdaten/PlanKl%Y%m%d.xml"
    Lehrer  = "{schulnummer}/moble/mobdaten/Lehrer.xml"
    PlanLe  = "{schulnummer}/moble/mobdaten/PlanLe%Y%m%d.xml"
    Raeume  = "{schulnummer}/mobra/mobdaten/Raeume.xml"
    PlanRa  = "{schulnummer}/mobra/mobdaten/PlanRa%Y%m%d.xml"

@dataclass
class VertretungsplanZugang():
    """Das VertretungsplanZugang-Objekt verwaltet den Zugang und das Abrufen
    von Daten über Zugangsdaten zu einem Indiware-Vertretungsplan. Pro
    Instanz werden standardmäßig nur Vertretungspläne eines Typs abgerufen.
    Beliebige andere Dateien können aber dennoch durch Angabe des
    Dateipfads abgerufen werden.

    Üblicherweise ist stark begrenzt, welche Planart für einen Benutzer
    verfügbar ist. Schüler-Benutzer können deswegen in der Regel nur Klassenpläne
    abrufen. Lehrer- und Raumpläne können allerdings unter gewissen Verlusten aus
    den Klassenplänen rekonstruiert werden.

    Parameters:
        schulnummer (int): Schulnummer der Schule auf deren Plan zugegriffen werden soll
        benutzername (str): Benutzername des Benutzers über den zugegriffen werden soll
        passwort (str): Passwort des Benutzers über den zugegriffen werden soll
        domain (str): Domain des Servers, der die Vertretungsplandaten bereitstellt
        port (int): Port des Service, der die Vertretungsplandaten bereitstellt
        dateipfadschema (str):
            Schema der Pfade unter dem die Quelldateien abgerufen werden können.
            `{schulnummer}` sowie strptime-Direktiven können als Platzhalter verwendet werden.
            Die Standardpfade sind im Enumerator `Standardpfade` enthalten.
        parser (Parser): Standard-Parsing-Anweisungen, um die Eigenheiten des Planers zu
            berücksichtigen. Diese können bei jedem Abruf überschrieben werden.
    """
    
    schulnummer:      int
    benutzername:     str
    passwort:         str
    domain:           str    = "stundenplan24.de"
    port:             int    = None
    dateipfadschema:  str    = Standardpfade.PlanKl
    parser:           Parser = field(default_factory=Parser)
    
    def __post_init__(self):

        if self.domain.endswith('/'):
            self.domain = self.domain[:-1]

        if "://" in self.domain:
            self.domain = self.domain.split("://")[-1]
            
        if self.dateipfadschema.startswith("/"):
            self.dateipfadschema = self.dateipfadschema[1:]

    @property
    def socket(self) -> URL:
        return URL.build(
            scheme="http",
            user=self.benutzername,
            password=self.passwort,
            host=self.domain,
            port=self.port
        )

    def __repr__(self):
        return f"<Vertretungsplan {self.benutzername}@{self.schulnummer}>"

    @overload
    def get(self, datum: date, *, datei: str = ..., parser: Parser = ...) -> Vertretungsplan: ...
    @overload
    def get(self, datei: str, *, datum: date = ..., parser: Parser = ...) -> Vertretungsplan: ...
    @overload
    def get(self, *, datum: date = ..., datei: str = ..., parser: Parser = ...) -> Vertretungsplan: ...

    def get(self, datum_or_datei: date | str = None, *, datum: date = None, datei: str = None, parser: Parser = None) -> Vertretungsplan:
        """Ruft den Vertretungsplan eines Tages ab. Es wird eine HTTP-Request von wenigen hundert Kilobyte ausgelöst.

        Parameters:
            datum (date): Datum des abzurufenden Tags
            datei (str): Pfad der abzurufenden Datei (beginnend nach der Domain). Wenn
                sowohl `datum` als auch `datei` angegeben sind, wird das Datum aus `datum`
                in `datei` eingesetzt, falls letzteres strftime-Direktiven enthält.
            parser (Parser): Parsing-Anweisungen, um die Eigenheiten des Planers zu
                berücksichtigen (standardmäßig von `self.parser` übernommen)


        Raises:
            ResourceNotFound: Wenn für den Tag keine Daten verfügbar sind oder die
                verwendete Schulnummer nicht registriert ist
            Unauthorized: Wenn die Zugangsdaten keinen Zugriff auf die Datei haben

        Für beide Fehler gibt es verschiedene mögliche Ursachen, die in den
        entsprechenden Fehlerklassen genauer beschrieben sind.
        """
        if isinstance(datum_or_datei, date):
            datum = datum_or_datei
        elif isinstance(datum_or_datei, str):
            datei = datum_or_datei
        elif datum_or_datei is not None:
            raise TypeError(f"Erstes Argument muss 'date' oder 'str' sein, nicht '{type(datum_or_datei).__name__}'")

        if datum is None:
            datum = date.today()

        if parser is None:
            parser = self.parser

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
            return Vertretungsplan.from_xml(XML.fromstring(response.content), parser=parser)
        
    def getall(self, referenzplan: str = Standardpfade.Klassen, nur_zukünftige: bool = False, wochenenden: bool = False) -> list[Vertretungsplan]:
        """Ruft die Vertretungspläne für alle verfügbaren Tage ab. Genauer gesagt wird
        versucht, jeden Tag im Zeitraum von 14 Tagen vor bis 7 Tagen nach dem zuletzt
        veröffentlichten Tag abzurufen. Jeder erhaltene Tag fordert wenige hundert Kilobyte.

        Parameters:
            referenzplan (str): Pfad, unter dem definitiv ein Plan vorhanden ist
            nur_zukünftige (bool): Ob nur zukünftige Tage abgerufen werden sollen
            wochenenden (bool): Ob auch Wochenenden abgerufen werden sollen
        """

        standard = self.get(datei=referenzplan)

        results: list[Vertretungsplan] = []

        for tag in (tag for tag in ((standard.datum or date.today()) + timedelta(days=i) for i in range(-7, 15))
                    if tag not in standard.freieTage
                    and (wochenenden or tag.weekday() < 5)
                    and (not nur_zukünftige or tag >= date.today())
        ):
            try:
               results.append(self.get(tag))
            except VpMobilPyError:
                continue

        return results


    def get_vpinfok(self) -> tuple[date, time, tuple[date]]:
        """Ruft die Daten der `vpinfok.txt` ab."""

        dateipfad = f"{self.schulnummer}/mobil/mobdaten/vpinfok.txt"

        response = requests.get(str(self.socket / dateipfad))
        response.raise_for_status()

        status = response.status_code
        if status == 401:
            raise Unauthorized(message=f"Zugangsdaten haben keinen Zugriff auf '{dateipfad}'", response=response)
        elif status == 404:
            raise ResourceNotFound(message=f"Datei '{dateipfad}' existiert nicht", response=response)
        else:
            response.raise_for_status()
            config = configparser.ConfigParser()
            config.read_string(response.text)
            Grunddaten = config["Grunddaten"]
            return (
                datetime.strptime(Grunddaten.get("Datum"), "%d.%m.%Y").date() if Grunddaten.get("Datum") else None,
                datetime.strptime(Grunddaten.get("Uhrzeit"), "%H:%M:%S").time() if Grunddaten.get("Uhrzeit") else None,
                tuple(
                    datetime.strptime(Grunddaten[key], "%Y%m%d").date() for key in Grunddaten if key.startswith("Plan")
                )
            )
                
        
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