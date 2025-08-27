# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import Vertretungsplan, VertretungsTag, Klasse, Stunde, Kurs

vp = Vertretungsplan()
day = VertretungsTag()
klasse = Klasse()
stunde = Stunde()
kurs = Kurs()

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
stunde.raum

kurs.fach
kurs.gruppe
kurs.kursnummer
kurs.lehrer