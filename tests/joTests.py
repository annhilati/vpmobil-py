from vpmobil import Vertretungsplan

vertretPlan = Vertretungsplan(10126582, "schueler", "s361o97")

#vertretPlan = Vertretungsplan(10161782, "schueler", "23LgS24")

tag = vertretPlan.fetch(20240612)
print(tag.lehrerKrank())

print(tag.klasse("9a").kurseInPeriode(3)[0].lehrer)
print(tag.klasse("9a").stundenInPeriode(3)[0].lehrer)
#print(tag.klasse("9a").alleStunden()[1].lehrer)
print(tag.klasse("9a").alleKurseHeute()[1].lehrer)
#tag.klasse("9a").alleStundenRegulaer()

klassen = ["5a", "5b", "5c", "6a", "6b", "6c", "7a", "7b", "7c", "8a", "8b", "8c", "9a", "9b", "9c", "10a", "10b", "10c"]

for kl in klassen:
    for std in tag.klasse(kl).stunden():
        print(kl + " - " + str(std.nr) + ": OK")