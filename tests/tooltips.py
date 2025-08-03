# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import Vertretungsplan, VpDay, Klasse, Stunde, Kurs

vp = Vertretungsplan()
day = VpDay()
klasse = Klasse()
stunde = Stunde()
kurs = Kurs()

vp.fetch()
vp.fetchall()

day.datei
day.datum
day.klasse()
day.klassen
day.saveasfile()
day.lehrerKrank
day.freieTage
day.zusatzInfo
day.zeitstempel

klasse.stundenHeute
klasse.stundenHeuteInPeriode()
klasse.kürzel
klasse.kurse
klasse.kurs()

stunde.geändert
stunde.ausfall
stunde.beginn
stunde.besonders
stunde.ende
stunde.fach
stunde.info
stunde.kursnummer
stunde.lehrer
stunde.periode
stunde.raum

kurs.fach
kurs.gruppe
kurs.kursnummer
kurs.lehrer

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

    ### Methode:
        .fetch(): Ruft die Daten eines Tages ab
    """