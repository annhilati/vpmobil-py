from vpmobil import Vertretungsplan

import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import pytz

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

# for d in range(20240612, 20240620):
#      try:
#          day = vertretungsplan.fetch(d)
#          try:
#              print(day.lehrerKrank())
#          except:
#              print(f"Error der Lehrer an {d}")
#      except:
#          print(f"Kein Plan für {d}")

#print(vertretungsplan.fetch(20240614).lehrerKrank())
TZ = pytz.timezone('Europe/Berlin')

def send_message():
    print("Nachricht wird versucht zu senden")
    
    vp = Vertretungsplan(10126582, "schueler", "s361o97")
    timezone = pytz.timezone('Europe/Berlin')
    unix_time = int(datetime.now(timezone).timestamp())

    try:
        #gesuchterTag = vp.fetch(20240805)  # Vertretungsplan.fetch -> vp.fetch korrigiert
        gesuchterTag = vp.fetch(20240619)  # Vertretungsplan.fetch -> vp.fetch korrigiert

        stunden = gesuchterTag.klasse("10a").alleStunden()
        liste = []
        for stunde in stunden:
            liste.append(f"{stunde.nr}: {stunde.fach} | {stunde.lehrer} | {stunde.raum}")
        display = "\n".join(liste)
        MESSAGE = f"""
## <:Allowed:1137799137497206854> Vertretungsplan-Scrape-Versuch am <t:{unix_time}:F>
<@720992368110862407> <@756842180399595560>

Erfolg! Für den <t:1720718940:D> (der erste Tag im SJ 24/25) liegt ein Vertretungsplan vor!

```\n{display}\n```"""

    except Exception as e:
        MESSAGE = f"""
## <:Forbidden:1137799141007818832> Vertretungsplan-Scrape-Versuch am <t:{unix_time}:F>
<@720992368110862407> <@756842180399595560>

Fehler! Für den <t:1720718940:D> (der erste Tag im SJ 24/25) liegt kein Vertretungsplan vor:
```{str(e)}```"""
    
    print(MESSAGE)
    
send_message()