import xml.etree.ElementTree as ET
from vpmobil import *
from datetime import date

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

#tag = vertretungsplan.fetch(date=20240619)
tag = vertretungsplan.fetch()

print(tag.getxml())
print(tag.freieTage())