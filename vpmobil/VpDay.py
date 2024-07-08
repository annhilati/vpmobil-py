from datetime import datetime, date
#Modules shall be imported as a 3-letter code
import xml.etree.ElementTree as XML 

from .Exceptions import XMLError

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         VpDay                                            │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class VpDay():
    """
    Enthält alle Daten für einen bestimmten Tag
    
    #### Attribute & Methoden
    - .zeitstempel
    - .zusatzInfo
    - .getxml()
    - .klasse()
    - .freieTage()
    """

    def __init__(self, xmldata: XML.ElementTree | bytes | str):
        self.datatree: XML.ElementTree = xmldata if isinstance(xmldata, XML.ElementTree) else XML.ElementTree(XML.fromstring(xmldata))
        self.rootVpMobil: XML.Element = self.datatree.getroot()
        self.zeitstempel: datetime = datetime.strptime(self.datatree.find('Kopf/zeitstempel').text, "%d.%m.%Y, %H:%M")
        "Gibt den Zeitpunkt zurück, zu dem der Vertretungsplan veröffentlicht wurde"

        ziZeilen = []
        for zusatzInfo in self.rootVpMobil.findall('.//ZusatzInfo'):
            for ziZeile in zusatzInfo.findall('.//ZiZeile'):
                if ziZeile.text:
                    ziZeilen.append(ziZeile.text)
        self.zusatzInfo = '\n'.join(ziZeilen)
        "Gibt die Zusatzinformationen des Tages zurück"

    def getxml(self, format: str = "ElementTree") -> (XML.ElementTree | str):
        """
        Gibt alle Daten für den Tag in einem bestimmten Format zurück

        - format: Das Format, in dem die Daten ausgegeben werden sollen. Eines von "str" oder "ElementTree".
        """

        match format:
            case "str":
                return XML.tostring(self.datatree.getroot(), encoding="utf-8", method="xml").decode('utf-8')
            case "ElementTree":
                return self.datatree
            case _:
                raise SyntaxError(f"Nicht unterstütztes Format: {format}")
            
    def klasse(self, kürzel: str):
        """
        Gibt ein Klassen-Objekt zurück, dass alle Daten über die Klasse enthält
        Ein Fehler wird ausgegeben, wenn die angegebene Klasse nicht gefunden werden kann. 

        - kürzel: Kürzel der zu suchenden Klasse (z.B. "8b")
        """

        for kl in self.rootVpMobil.findall('.//Kl'):
            kurz = kl.find('Kurz')
            if kurz is not None and kurz.text == kürzel:
                return Klasse(xmldata=kl)
        raise XMLError(f"Keine Klasse {kürzel} gefunden")

    def freieTage(self) -> list[date]:
        "Gibt eine Liste der im Plan als frei markierten Tage zurück"

        freieTage = self.rootVpMobil.find("FreieTage")
        if freieTage is None:
            raise XMLError("Element 'FreieTage' nicht in den XML-Daten gefunden")
        
        freieTageList: list[date] = []
        for ft in freieTage.findall("ft"):
            if ft.text is not None:
                freieTageList.append(datetime.strptime(ft.text, "%y%m%d").date())
        return freieTageList

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Klasse                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Klasse():
    """
    Enthält alle Daten für eine bestimmte Klasse

    #### Attribute & Methoden
    - .getxml()
    - .stunde()
    - .stunden()
    - .alleStunden()
    """

    def __init__(self, xmldata: XML.Element):
        self.data: XML.Element = xmldata

    def getxml(self, format: str = "Element") -> (XML.Element | str):
        """
        Gibt alle Daten der Klasse in einem bestimmten Format zurück

        - format: Das Format, in dem die Daten ausgegeben werden sollen. Eines von "str" oder "ElementTree".
        """

        match format:
            case "str":
                return XML.tostring(self.data(), encoding="utf-8", method="xml").decode('utf-8')
            case "Element":
                return self.data
            case _:
                raise SyntaxError(f"Nicht unterstütztes Format: {format}")

    def stunde(self, nr: int): # macht diese Funktion Sinn? Wer braucht denn random nur den ersten Kurs?
        """
        Gibt die erste Stunde mit der angegebenen Nummer zurück.
        Gibt einen Fehler aus, wenn die Stunde nicht existiert
        """

        plan = self.data.find("Pl")
        for std in plan.findall("Std"):
            st = std.find("St")
            if st is not None and st.text == str(nr):
                return Stunde(std)
        raise XMLError("Stunde wurde nicht gefunden!")

    def stunden(self, nr: int):
        """
        Gibt alle Stunden zurück, die in der angegebenen Stunde stattfinden.
        Hilfreich, wenn mehrere Fächer zur selben Zeit stattfinden.
        Gibt einen Fehler zurück, wenn die angegebene(n) Stunde(n) nicht existieren
        """

        fin: list[Stunde] = []
        plan = self.data.find("Pl")
        for std in plan.findall("Std"):
            st = std.find("St")
            if st is not None and st.text == str(nr):
                fin.append(Stunde(xmldata=std))
        if len(fin) != 0:
            return fin
        else:
            raise XMLError("Keine Stunden mit dieser Nummer gefunden!")
    
    def alleStunden(self):
        """
        Gibt alle Stunden, welche die Klasse an diesem Tag hat zurück.
        """

        fin: list[Stunde] = []
        plan = self.data.find("Pl")
        for std in plan.findall("Std"):
            st = std.find("St")
            if st is not None:
                fin.append(Stunde(std))
        if len(fin) != 0:
            return fin
        else:
            raise XMLError("Keine Stunden bei dieser Klasse gefunden!")

# ╭──────────────────────────────────────────────────────────────────────────────────────────╮
# │                                         Stunde                                           │ 
# ╰──────────────────────────────────────────────────────────────────────────────────────────╯

class Stunde():
    """
    Enthält Informationen über eine bestimmte Stunde

    #### Attribute & Methoden
    - .nr
    - .beginn
    - .ende
    - .anders
    - .ausfall
    - .fach
    - .lehrer
    - .raum
    - .info
    - .kursnummer
    """

    def __init__(self, xmldata: XML.Element | bytes | str):
        self.data: XML.Element = xmldata if isinstance(xmldata, XML.Element) else XML.Element(XML.fromstring(xmldata))
        self.nr: int = int(self.data.find("St").text)
        "Nummer der Stunde"

        self.beginn: str = str(self.data.find("Beginn").text)
        "Beginn der Stunde als str"

        self.ende: str = str(self.data.find("Ende").text)
        "Ende der Stunde als str"

        if "FaAe" in self.data.find("Fa").attrib or "RaAe" in self.data.find("Ra").attrib or "LeAe" in self.data.find("Le").attrib:
            anders = True
        else:
            anders = False
        self.anders: bool = anders
        "Gibt an, ob irgendeine Eigenschaft dieser Stunde vom Regelplan abgeändert wurde"

        if self.data.find("Fa").text == "---":
            ausfall = True
        else:
            ausfall = False
        self.ausfall: bool = ausfall
        """
        Gibt an, ob die Stunde entfällt. 
        Wenn ja, werden 'lehrer', 'fach' und 'raum' leere Strings zurückgeben
        """

        self.fach: str = self.data.find("Fa").text if self.ausfall == False else ""
        """
        Gibt das Fach, welches in dieser Stunde stattfindet zurück.
        Gibt einen leeren String zurück, wenn die Stunde entfällt
        """

        self.lehrer: str = self.data.find("Le").text if self.ausfall == False else ""
        """
        Gibt den Lehrer, welcher diese Stunde hält zurück.
        Gibt einen leeren String zurück, wenn die Stunde entfällt
        """

        self.raum: str = self.data.find("Ra").text if self.ausfall == False else ""
        """
        Gibt den Raum, in dem diese Stunde stattfindet zurück.
        Gibt einen leeren String zurück, wenn die Stunde entfällt
        """

        self.info: str = self.data.find("If").text
        """
        Gibt eine optionale vom Planer verfasste Information zu dieser Stunde.
        Ist nur in besonderen Situationen und bei entfallen der Stunde vorhanden
        """

        self.kursnummer: int = int(self.data.find("Nr").text)
        """
        Gibt die Nummer des Kurses zurück.
        Nützlich für das Kurs() Objekt
        """