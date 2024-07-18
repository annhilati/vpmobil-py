# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import Vertretungsplan, VpDay, Klasse, Stunde

vp = Vertretungsplan()
day = VpDay()
klasse = Klasse()
stunde = Stunde()


vp.fetch()

day.getxml()
day.klasse()
day.freieTage()
day.zusatzInfo
day.zeitstempel

klasse.alleStunden()
klasse.stunde()
klasse.stunden()

stunde.anders
stunde.ausfall
stunde.beginn
stunde.ende
stunde.fach
stunde.info
stunde.kursnummer
stunde.lehrer
stunde.nr
stunde.raum

class Test():
    """
    Enthält die notwendigen Daten um auf einen stundenplan24.de-Vertretungsplan zuzugreifen

    ### Argumente:
        schulnummer (int): Schulnummer des Vertretungsplans
        benutzer (str): Benutzername des Benutzers über den zugegriffen werden soll
        passwort (str): Passwort des Benutzers über den zugegriffen werden soll
        url (str): URL und Verzeichnispfad, an dem die Quelldateien gespeichert werden
        dateinamensschema (str): Schema der Namen der Quelldateien
            z.B. `PlanKl%Y%m%d.xml`. Es können [Platzhalter des datetime-Moduls](https://strftime.org/) verwendet werden
    """
svbbc
    """
    

    #### Argumente
    - 
    - benutzer (str)
    - passwort (str)
    - url (str): Pfad des Speicherorts der XML-Quelldateien. Platzhalter:
        - {schulnummer}
    - dateinamensschema (str): z.B `PlanKl%Y%m%d.xml`. Nutze Zeitplatzhalter des datetime-Moduls: 
        - %Y: Jahr (24)
        - %m: Monat (05)
        - %d: Tag (07)

    #### Attribute & Methoden
    - .fetch()
    """