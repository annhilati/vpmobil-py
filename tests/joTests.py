from vpmobil import Vertretungsplan

vertretPlan = Vertretungsplan(10126582, "schueler", "s361o97")

tag = vertretPlan.fetch(20240612)
print(tag.lehrerKrank())