from vpmobil import Vertretungsplan, VpMobil, VpDay, Klasse
import xml.etree.ElementTree as XML
from acemeta import fileToStr
import requests

from vpmobil import Vertretungsplan

vp = Vertretungsplan(10126582, "schueler", "s361o97")
vp1 = Vertretungsplan(10161728, "schueler", "23LgS24")

pläne = vp.fetchall()

print(pläne)