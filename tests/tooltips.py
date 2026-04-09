# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import *

vp       = Vertretungsplan()
day      = VertretungsplanNEU()
klasse   = Klasse()
lehrer   = Lehrer()
raum     = Raum()
stunde   = Stunde()
kurs     = Kurs()
aufsicht = Aufsicht()
klausur  = Klausur()

Standardpfade

vp.get()

day.from_xml()
day.fromfile()
day.as_dict()
day.saveasfile()
day.datei
day.datum
day.zeitstempel
day.zusatzinfo
day.freieTage
day.stunden
day.kurse
day.klausuren
day.aufsichten
day.zeitplan
day.lehrerKrank
day.klassen
day.lehrer
day.räume
day.freieRäume()

stunde.fach
stunde.fachmeta
stunde.fachänderung
stunde.klassen
stunde.klassenänderung
stunde.lehrer
stunde.lehreränderung
stunde.räume
stunde.raumänderung
stunde.ausfall
stunde.änderung
stunde.beginn
stunde.ende
stunde.info
stunde.kursnummer
stunde.periode

klasse.kürzel
klasse.stunden
klasse.kurse
klasse.klausuren

lehrer.kürzel
lehrer.stunden
lehrer.kurse
lehrer.aufsichten

raum.kürzel
raum.stunden

aufsicht.lehrer
aufsicht.ortinfo
aufsicht.zeitinfo
aufsicht.vorStunde
aufsicht.beginn

klausur.beginn
klausur.dauer
klausur.info
klausur.kurse
klausur.lehrer
klausur.periode

kurs.kursnummer
kurs.fach
kurs.kürzel
kurs.lehrer