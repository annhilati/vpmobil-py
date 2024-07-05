import xml.etree.ElementTree as ET
from vpmobil import Vertretungsplan

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

#tag = vertretungsplan.fetch(date=20240619)
tag = vertretungsplan.fetch(date=20240619)

print(tag.getxml())
print(tag.zeitstempel())