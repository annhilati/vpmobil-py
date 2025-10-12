# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import *

vp =   Vertretungsplan()
day =  VertretungsTag()         # Tag <- Klassen <- Stunden <- Fa, Le, Ra, FaAe, LeAe, ...
day1 = RaumVertretungsTag()     # Tag <- Räume   <- Stunden <- Fa, Le, Kl, FaAe, LeAe, ...
day2 = LehrerVertretungsTag()   # Tag <- Lehrer  <- Stunden <- Fa, Kl, Ra, FaAe, LeAe, ...
klasse = Klasse()
raum = Raum()
lehrer = Lehrer()
stunde = Stunde()
kurs = Kurs()
aufsicht = Aufsicht()

vp.fetch()

day.datei
day.datum
day.klasse()
day.klassen
day.saveasfile()
day.lehrerKrank
day.freieTage
day.zusatzInfo
day.zeitstempel

day1.räume
day1.raum()

day2.lehrer
day2.get_lehrer()

klasse.stunden
klasse.stundenInPeriode()
klasse.kürzel
klasse.kurse
klasse.kurs()

lehrer.aufsichten

aufsicht.ort
aufsicht.uhrzeit
aufsicht.vorStunde
aufsicht.zeit

stunde.geändert
stunde.ausfall
stunde.beginn
stunde.ende
stunde.fach
stunde.info
stunde.kursnummer
stunde.periode
stunde.lehrer
stunde.räume
stunde.klassen

kurs.fach
kurs.kürzel
kurs.kursnummer
kurs.lehrer