from vpmobil import Vertretungsplan

import xml.etree.ElementTree as ET
from datetime import date

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

tag = vertretungsplan.fetch(date=20240619)

stunden = tag.klasse("9a").stundenInPeriode(1)
for stunde in stunden:
    print(stunde.beginn, stunde.fach, stunde.lehrer, stunde.raum)