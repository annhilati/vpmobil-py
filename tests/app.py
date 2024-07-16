from vpmobil import Vertretungsplan, VpMobil
import os

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

day = vertretungsplan.fetch(20240619)

print(day.datum)