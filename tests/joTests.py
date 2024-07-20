from vpmobil import Vertretungsplan

vertretPlan = Vertretungsplan(10126582, "schueler", "s361o97")

tag = vertretPlan.fetch(20240612)
print(tag.lehrerKrank())

print(tag.klasse("9a").kurseInPeriode(3)[0].lehrer)
print(tag.klasse("9a").stundenInPeriode(3)[0].lehrer)
print(tag.klasse("9a").alleStunden()[1].lehrer)
print(tag.klasse("9a").alleKurseHeute()[1].lehrer)
tag.klasse("9a").alleStundenRegulaer()