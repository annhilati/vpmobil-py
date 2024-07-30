from vpmobil import Vertretungsplan, VpMobil, VpDay, Klasse
import xml.etree.ElementTree as XML
from acemeta import fileToStr
import requests

from vpmobil import Vertretungsplan

vp = Vertretungsplan(10126582, "schueler", "s361o97")

file = vp.fetch(datum=20240619)