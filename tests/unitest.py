from vpmobil import Vertretungsplan
from datetime import datetime

klassen = ["5a", "5b", "5c", "6a", "6b", "6c", "7a", "7b", "7c", "8a", "8b", "8c", "9a", "9b", "9c", "10a", "10b", "10c"]

print("UNITEST - START")
print(33*"-")
print("Wilkommen beim Unitest! Dieses Programm testet ein gesamtes Vertretungsplan-Objekt und gibt am Ende eine übersicht der Funktionsweise der vpmobil-py Package aus.")
print(33*"-")
print("Schuljahr: 2025/2026")
schulNr = int(input("Bitte Schulnummer eingeben: "))
schulPass = input("Bitte Passwort eingeben: ")
vertretPlan = Vertretungsplan(schulNr, "schueler", schulPass)
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
day = 20
month = 6
dat = "20250620"
testVar = ""
endNow = False
while endNow == False:
    print("UNITEST - Check " + dat, end="\r")
    try:
        tag = vertretPlan.fetch(datetime.strptime(dat, "%Y%m%d").date())
    except:
        keinPln += 1
    else:
        pln += 1
        for kl in klassen:
            for st in tag.klasse(kl).stundenHeute:
                for std in tag.klasse(kl).stundenHeute[st]:
                    gesStd += 1
                    try:
                        testVar = kl + str(std.beginn) + str(std.ende) + str(std.lehrer) + str(std.fach) + str(std.raum) + str(std.periode) + str(std.kursnummer)
                    except Exception as e:
                        # raise e # DEBUG
                        print("UNITEST - FEHLER - " + "Klasse " + kl + ", Stunde " + str(std.periode) + " am Tag " + dat)
                        gesErr += 1
                    else:
                        okStd += 1
        try:
            testVar = str(tag.freieTage)
        except:
            print("UNITEST - FEHLER - tag.freieTage() am Tag " + dat)
            print(testVar)
        try:
            testVar = str(tag.lehrerKrank)
        except:
            print("UNITEST - FEHLER - tag.lehrerKrank am Tag " + dat)
            print(testVar)
        try:
            testVar = tag.datei + " " + str(tag.datum) + " " + str(tag.zeitstempel) + " " + str(tag.zeitstempel) + " " + tag.zusatzInfo
        except:
            print("UNITEST - FEHLER - einer von .datei, .datum, .wochentag, .zeitstempel, .zusatzinfo am Tag " + dat)
            print(testVar)
    finally:
        if dat == "20250710":
            endNow = True
            break
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
            dat = "2025" + "0" + str(month)
        else:
            dat = "2025" + str(month)
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