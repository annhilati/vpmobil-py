from vpmobil import Vertretungsplan, VpMobil, VpDay, Klasse
import xml.etree.ElementTree as XML
import os

from vpmobil import Vertretungsplan

vp = Vertretungsplan(10126582, "schueler", "s361o97")

tag = vp.fetch(20240618)
klasse = tag.klasse("10a")

stunden = klasse.alleStunden()

for stunde in stunden:
  print(f"{stunde.nr}: {stunde.fach} bei {stunde.lehrer} in {stunde.raum}")