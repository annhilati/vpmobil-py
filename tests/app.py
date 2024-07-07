from vpmobil import Vertretungsplan

import xml.etree.ElementTree as ET
from datetime import date

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

tag = vertretungsplan.fetch(date=20240618)

print(tag.zusatzInfo)