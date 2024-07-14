from vpmobil import Vertretungsplan, VpMobil
import os

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

day = vertretungsplan.fetch(20240619)

day.saveasfile(pfad=f"./{day.datum}.xml")

# absolute_path = os.path.abspath("./datei.xml")
# xml.write(absolute_path, encoding="utf-8", xml_declaration=True)