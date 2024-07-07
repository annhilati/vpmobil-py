import VpDay as vp
import Vertretungsplan as vt

vertretPlan = vt.Vertretungsplan(10126582, "schueler", "s361o97")

tag = vertretPlan.fetch(20240619)

kl = tag.klasse("9a")

testStd = kl.alleStunden()

for std in testStd:
    print(std.fach, std.lehrer, std.raum)