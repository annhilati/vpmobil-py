# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import *
from vpmobil.extensions.reparser import *
from vpmobil.models import KlasseLikeBase, KlasseLikeType, VertretungsTagType

VertretungsTag()
vp =   Vertretungsplan()
day =  KlassenVertretungsTag()         # Tag <- Klassen <- Stunden <- Fa, Le, Ra, FaAe, LeAe, ...
day1 = RaumVertretungsTag()    # Tag <- Räume   <- Stunden <- Fa, Le, Kl, FaAe, LeAe, ...
day2 = LehrerVertretungsTag()   # Tag <- Lehrer  <- Stunden <- Fa, Kl, Ra, FaAe, LeAe, ...
klasse  = Klasse()
raum    = Raum()
lehrer  = Lehrer()
stunde  = Stunde()
kurs    = Kurs()
aufsicht = Aufsicht()

Stundenplan24Pfade

vp.fetch()

day.datei
day.datum
day.zeitstempel
day.zusatzInfo
day.saveasfile()
day.fromfile()
day.freieTage

day.klassen
day.klasse()
day.lehrerKrank

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
stunde.lehrergeändert
stunde.raumgeändert
stunde.klassegeändert
stunde.fachgeändert
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

kurs.kursnummer
kurs.fach
kurs.kürzel
kurs.lehrer