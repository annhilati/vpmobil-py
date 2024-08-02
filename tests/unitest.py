from vpmobil import Vertretungsplan

vertretPlan = Vertretungsplan(10126582, "schueler", "s361o97")

#vertretPlan = Vertretungsplan(10161728, "schueler", "23LgS24")

klassen = ["5a", "5b", "5c", "6a", "6b", "6c", "7a", "7b", "7c", "8a", "8b", "8c", "9a", "9b", "9c", "10a", "10b", "10c"]

print("UNITEST - START")
print(33*"-")
print("Wilkommen beim Unitest! Dieses Programm testet ein gesamtes Vertretungsplan-Objekt und gibt am Ende eine übersicht der Funktionsweise der vpmobil-py Package aus.")
print(33*"-")
print("Schuljahr: 2024/2025")
print("Zugangsdaten: Bereit")
print("Unitest: Bereit")
print(33*"-")
print("Bitte ENTER zum starten drücken.")
input("->")

print("UNITEST - Working...")
pln = 0
keinPln = 0
klOk = 0
gesErr = 0
gesStd = 0
okStd = 0
day = 1
month = 1
dat = "20240612"
testVar = ""
while 7==7:
    print("UNITEST - Check " + dat, end="\r")
    try:
        tag = vertretPlan.fetch(int(dat))
    except:
        keinPln += 1
    else:
        pln += 1
        for kl in klassen:
            for std in tag.klasse(kl).stunden():
                gesStd += 1
                try:
                    testVar = kl + std.beginn + std.ende + std.lehrer + std.fach + str(std.raum) + str(std.nr) + str(std.kursnummer)
                except:
                    print("UNITEST - FEHLER - " + "Klasse " + kl + ", Stunde " + str(std.nr) + " am Tag " + dat)
                    gesErr += 1
                else:
                    okStd += 1
        try:
            testVar = str(tag.freieTage())
        except:
            print("UNITEST - FEHLER - tag.freieTage() am Tag " + dat)
        try:
            testVar = str(tag.lehrerKrank())
        except:
            print("UNITEST - FEHLER - tag.lehrerKrank am Tag " + dat)
        try:
            testVar = tag.datei + " " + str(tag.datum) + " " + str(tag.wochentag) + " " + str(tag.zeitstempel) + " " + tag.zusatzInfo
        except:
            print("UNITEST - FEHLER - einer von .datei, .datum, .wochentag, .zeitstempel, .zusatzinfo am Tag " + dat)
    finally:
        if day == 31:
            day = 1
            month += 1
        else:
            day += 1
        #end
        if month > 12:
            break
        #new date
        if month<10:
            dat = "2024" + "0" + str(month)
        else:
            dat = "2024" + str(month)
        if day<10:
            dat = dat + "0" + str(day)
        else:
            dat = dat + str(day)

print("UNITEST - DONE")
print(33*"-")
print("Ergebnisse:")
print("Insgesamt Geprüfte Tage: " + str(pln + keinPln))
print("   Davon Verfügbar: " + str(pln))
print("   Davon nicht Verfügbar: " + str(keinPln))
print("Insgesamt geprüfte Stunden: " + str(gesStd))
print("   Davon Fehler: " + str(gesErr))
print("   Davon Ok: " + str(okStd))
print("Alle Funktionen geprüft bei " + str(pln) + " Tagen Ok")
print(33*"-")
print("UNITEST - END")