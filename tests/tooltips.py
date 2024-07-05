# In dieser Datei können Tooltips, Docstrings und Typehints getestet werden

from vpmobil import Vertretungsplan, VpDay

vp = Vertretungsplan()
vp.fetch()
vp.schulnummer 

day = VpDay()
day.getxml()
day.klasse()
day.freieTage()
day.zusatzInfo()
day.zeitstempel()