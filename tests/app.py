from vpmobil import Vertretungsplan, VpDay, Klasse
import xml.etree.ElementTree as XML
import requests

from vpmobil import Vertretungsplan

vp = Vertretungsplan(..., "schueler", ...)
vp1 = Vertretungsplan(..., "schueler", ...)

pläne = vp.fetchall()

for plan in pläne:
    plan.saveasfile(f"./tests/mobdaten/{plan.datum}.xml")