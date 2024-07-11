from vpmobil import Vertretungsplan

import xml.etree.ElementTree as ET
from datetime import date

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

for d in range(20240612, 20240620):
     try:
         day = vertretungsplan.fetch(d)
         try:
             print(day.lehrerKrank())
         except:
             print(f"Error der Lehrer an {d}")
     except:
         print(f"Kein Plan für {d}")

#print(vertretungsplan.fetch(20240614).lehrerKrank())