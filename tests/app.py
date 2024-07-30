from vpmobil import Vertretungsplan, VpMobil, VpDay, Klasse
import xml.etree.ElementTree as XML
from acemeta import fileToStr
import requests

from vpmobil import Vertretungsplan

vp = Vertretungsplan(10126582, "schueler", "s361o97")
vp1 = Vertretungsplan(10161728, "schueler", "23LgS24")

tag = vp.fetch(20240619)

lis = tag.klassen()

for kl in lis:
    print(f"{kl.kürzel}")

# for date in range(20240701, 20240730):
#     try:
#         tag = vp1.fetch(date)
#         tag.saveasfile(f"./scrap/{date}.xml")
#     except VpMobil.FetchingError:
#         print(f"{date} konnte keinen Plan hervorbringen")