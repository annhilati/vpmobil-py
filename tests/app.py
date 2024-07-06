from vpmobil import Vertretungsplan

import xml.etree.ElementTree as ET
from datetime import date

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

#tag = vertretungsplan.fetch(date=20240619)
for day in range(20240614, 20240619):
    try:
        tag = vertretungsplan.fetch(day)
        print(f"{day}: \n{tag.zusatzInfo}")
    except:
        print(f"{day}: nix plan")

