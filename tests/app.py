from vpmobil import Vertretungsplan, VpMobil

vertretungsplan = Vertretungsplan(10126582, "schueler", "s361o97")

for d in range(20240612, 20240620):
    try:
        day = vertretungsplan.fetch(d)
        try:
            print(day.lehrerKrank())
        except VpMobil.XMLParsingError:
            print(f"Error der Lehrer an {d}")
    except:
        print(f"Kein Plan für {d}")

print(vertretungsplan.fetch(20240614).lehrerKrank())