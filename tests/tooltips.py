# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import Vertretungsplan, VpDay, Stunde

vp = Vertretungsplan()
day = VpDay()
stunde = Stunde()


vp.fetch()
vp.schulnummer 

day.getxml()
day.klasse()
day.freieTage()
day.zusatzInfo
day.zeitstempel