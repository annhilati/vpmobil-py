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