# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import *

vp = Vertretungsplan()
day = VertretungsTag()
day1 = RaumVertretungsTag()
day2 = LehrerVertretungsTag()
klasse = Klasse()
raum = Raum()
lehrer = Lehrer()
stunde = Stunde()
kurs = Kurs()
aufsicht = Aufsicht()

vp.fetch()
vp.bulkfetch()

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
stunde.ende
stunde.fach
stunde.info
stunde.kursnummer
stunde.lehrer
stunde.periode
stunde.räume
stunde.klassen

kurs.fach
kurs.gruppe
kurs.kursnummer
kurs.lehrer