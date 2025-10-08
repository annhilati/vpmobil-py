from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as XML
from typing import Literal
from datetime import datetime, date
import re

from vpmobil.utils import prettyxml

@dataclass
class VertretungsTagBase():
    """Base-Class für Vertretungspläne an einem bestimmten Tag.

    Beim Versuch einer Instanzierung wird automatisch eine Instanz von `VertretungsTag`, `LehrerVertretungsTag` oder `RaumVertretungsTag` zurückgegeben.
    """

    _data: XML.ElementTree

    def __new__(cls, _data: XML.ElementTree):
        if _data.find(".//planart") is None or _data.find(".//planart").text is None:
            raise ValueError
        
        match _data.find(".//planart").text:
            case "K":
                return VertretungsTag(_data)
            case "L":
                return LehrerVertretungsTag(_data)
            case "R":
                return RaumVertretungsTag(_data)
            case _:
                raise ValueError
            
    def __repr__(self):
        return f"<Vertretungsplan (Typ {self.planart}) vom {self.datum.strftime('%d.%m.%Y')}>"
    
    @property
    def planart(self) -> Literal['K', 'L', 'R']:
        "Interne Bezeichnung für die Art des Inhalts des Plans"
        return self._data.find(".//planart").text
        
    @property
    def zeitstempel(self) -> datetime | None:
        "Veröffentlichungszeitpunkt des Vertretungsplans"
        element = self._data.find('Kopf/zeitstempel')
        if element is None or not element.text:
            return None
        return datetime.strptime(element.text, "%d.%m.%Y, %H:%M")
        
    @property
    def datei(self) -> str | None:
        "Dateiname der Quelldatei"
        element = self._data.find('Kopf/datei')
        if element is None or not element.text:
            return None
        return element.text

    @property
    def datum(self) -> date | None:
        "Datum für das der Vertretungsplan gilt"
        if match := re.search(r"(\d{4})(\d{2})(\d{2})", self.datei):
            year, month, day = map(int, match.groups())
            return date(year, month, day)
        return None
            
    @classmethod
    def fromfile(cls, pfad: Path) -> VertretungsTag | LehrerVertretungsTag | RaumVertretungsTag:
        """
        Erzeugt ein VertretungsTag-Objekt aus einer XML-Vertretungsplandatei

        Parameter
        ----------
        pfad: Path
            Dateipfad einer XML-Datei

        Raises
        ----------
        FileNotFoundError : Wenn die Datei nicht existiert
        ValueError : Wenn die Datei nicht gelesen werden kann
        """
        with open(pfad) as f:
            instance = cls(_data=XML.parse(f))
        return instance
    
    def saveasfile(self, pfad: Path | str = "./datei.xml", overwrite=False) -> None:
        """Speichert alle Daten des Tages als XML-Datei

        Parameter
        ---------
        pfad : Path | str
            Der Dateipfad der zu erstellenden Datei
        overwrite : bool
            Ob die Datei überschrieben werden darf, falls sie bereits existiert

        Raises
        --------
        FileExistsError : Falls eine bereits existierende Datei überschrieben werden soll, obwohl `overwrite` `False` ist
        """

        xmlpretty = prettyxml(self._data)

        zielpfad = Path(pfad).resolve() if isinstance(pfad, str) else pfad.resolve()
        zielverzeichnis = zielpfad.parent
        zielverzeichnis.mkdir(parents=True, exist_ok=True)

        if zielpfad.exists() and not overwrite:
            raise FileExistsError(f"Die Datei '{zielpfad}' existiert bereits.")

        zielpfad.write_text(xmlpretty, encoding="utf-8")


class VertretungsTag(VertretungsTagBase):
    ...

class LehrerVertretungsTag(VertretungsTagBase):
    ...

class RaumVertretungsTag(VertretungsTagBase):
    ...

test = VertretungsTagBase()