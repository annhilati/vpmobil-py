# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import *

vp       = VertretungsplanZugang()
day      = Vertretungsplan()
stunde   = Stunde()
kurs     = Kurs()
klausur  = Klausur()
aufsicht = Aufsicht()
klasse   = Klasse()
lehrer   = Lehrer()
raum     = Raum()

parser = Parser()
parser.clone()

Standardpfade

vp.socket
vp.get()
vp.get_all()
vp.get_vpinfok()

day.from_element_tree()
day.from_file()
day.as_dict()
day.export()
day.to_element_tree()
day.save_xml()
day.dateiname
day.datum
day.zeitstempel
day.zusatzinfo
day.freieTage
day.stunden
day.kurse
day.klausuren
day.aufsichten
day.zeitplan
day.abwesendeLehrer
day.klassen
day.lehrer
day.räume
day.freieRäume()

stunde.from_element()
stunde.to_element()
stunde.fach
stunde.fachmeta
stunde.fachänderung
stunde.klassen
stunde.klassenänderung
stunde.lehrer
stunde.lehreränderung
stunde.räume
stunde.raumänderung
stunde.beginn
stunde.ende
stunde.info
stunde.kursnummer
stunde.periode
stunde.ausfall
stunde.änderung

klasse.to_element()
klasse.kürzel
klasse.stunden
klasse.kurse
klasse.klausuren

lehrer.to_element()
lehrer.kürzel
lehrer.stunden
lehrer.kurse
lehrer.aufsichten

raum.to_element()
raum.kürzel
raum.stunden

aufsicht.from_element()
aufsicht.to_element()
aufsicht.lehrer
aufsicht.ortinfo
aufsicht.zeitinfo
aufsicht.vorStunde
aufsicht.beginn

klausur.from_element()
klausur.to_element()
klausur.beginn
klausur.dauer
klausur.info
klausur.kurse
klausur.lehrer
klausur.periode

kurs.from_element()
kurs.to_element()
kurs.kursnummer
kurs.klassen
kurs.fach
kurs.kürzel
kurs.lehrer