import VpDay as vp
import Vertretungsplan as vt

vertretPlan = vt.Vertretungsplan(10126582, "schueler", "s361o97")

tag = vertretPlan.fetch(20240619)

print(tag.lehrerKrank())