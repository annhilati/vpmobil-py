from vpmobil import Vertretungsplan

import xml.etree.ElementTree as ET
from datetime import date

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

#tag = vertretungsplan.fetch(date=20240619)
tag = vertretungsplan.fetch(20240619)

print(tag.klasse("11a"))