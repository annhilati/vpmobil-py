from vpmobil import Vertretungsplan, VpMobil, VpDay, Klasse
import xml.etree.ElementTree as XML
import os

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

day = vertretungsplan.fetch(20240619)
klasse = day.klasse("9a")
print(f"{klasse:str}")