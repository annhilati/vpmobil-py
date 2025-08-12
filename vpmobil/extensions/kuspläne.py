import json
from PyPDF2 import PdfReader
from pathlib import Path

def kurse(pfad: Path) -> dict[str, list[str]]:
    reader = PdfReader(pfad)

    seiten: list[str] = []

    for seite in reader.pages:
        seiten.append(seite.extract_text())

        
    
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

kurse = {"TEST": ["Jan", "Bo", "Karl"]}

for seite in seiten:
    for zeile in seite.splitlines():
        if "Freitag" in zeile:
            aktSchüler = zeile.split(",")[1]
        elif zeile[0].isnumeric():
            for kurs in zeile[1:].split():
                if has_numbers(kurs) and kurs[0].isalpha() and kurs[-2].isalpha():
                    if not kurs in kurse:
                        kurse[kurs] = []
                    if not aktSchüler in kurse[kurs]:
                        kurse[kurs].append(aktSchüler)
end = False
while end == False:
    printKurse = {}
    
    print("1 - Meine Kurse\n2 - Meine Kurse als Datei\n3 - Kurse mit zwei bestimmten Leuten\n4 - Kurse mit drei bestimmten Leuten\n5 - Ende")
    match input("-> "):
        case "1":
            nam = " " + input("Name eingeben: ")
            for key, val in kurse.items():
                if nam in val:
                    printKurse[key] = val
            print(json.dumps(printKurse))  
        case "2":
            nam = " " + input("Name eingeben: ")
            for key, val in kurse.items():
                if nam in val:
                    printKurse[key] = val
            with open(f"kurse_{nam}.json", "w") as f:
                f.write(json.dumps(printKurse))
        case "3":
            nam1 = " " + input("Name 1: ")
            nam2 = " " + input("Name 2: ")
            for key, val in kurse.items():
                if nam1 in val and nam2 in val:
                    printKurse[key] = val
            print(f"{len(printKurse)} Kurse mit{nam1} und{nam2}:")
            for key in printKurse:
                print(key)
        case "4":
            nam1 = " " + input("Name 1: ")
            nam2 = " " + input("Name 2: ")
            nam3 = " " + input("Name 3: ")
            for key, val in kurse.items():
                if nam1 in val and nam2 in val and nam3 in val:
                    printKurse[key] = val
            print(f"{len(printKurse)} Kurse mit{nam1},{nam2} und{nam3}:")
            for key in printKurse:
                print(key)
        case "5":
            end = True
            break
    print(40*"-")