from vpmobil import Vertretungsplan, VpMobil, VpDay, Klasse
import xml.etree.ElementTree as XML
import os

from vpmobil import Vertretungsplan

vp = Vertretungsplan(10126582, "schueler", "s361o97")

tag = vp.fetch(datum=20240619)

print(f"{tag:xml}")