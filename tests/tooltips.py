# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import *

vp       = VertretungsplanZugang()
day      = Vertretungsplan()
klasse   = Klasse()
lehrer   = Lehrer()
raum     = Raum()
stunde   = Stunde()
kurs     = Kurs()
aufsicht = Aufsicht()
klausur  = Klausur()

Standardpfade

vp.socket
vp.get()
vp.getall()

day.from_xml()
day.fromfile()
day.as_dict()
day.saveasfile()
day.to_xml()
day.save_source()
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

stunde.from_xml()
stunde.to_xml()
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

klasse.to_xml()
klasse.kürzel
klasse.stunden
klasse.kurse
klasse.klausuren

lehrer.to_xml()
lehrer.kürzel
lehrer.stunden
lehrer.kurse
lehrer.aufsichten

raum.to_xml()
raum.kürzel
raum.stunden

aufsicht.from_xml()
aufsicht.to_xml()
aufsicht.lehrer
aufsicht.ortinfo
aufsicht.zeitinfo
aufsicht.vorStunde
aufsicht.beginn

klausur.from_xml()
klausur.to_xml()
klausur.beginn
klausur.dauer
klausur.info
klausur.kurse
klausur.lehrer
klausur.periode

kurs.from_xml()
kurs.to_xml()
kurs.kursnummer
kurs.fach
kurs.kürzel
kurs.lehrer