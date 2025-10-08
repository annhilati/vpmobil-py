# Indiware

## Endpoints
```py
f"https://www.stundenplan24.de/{schoolcode}/wplan/wdaten/SPlanLe_Basis.xml"         # ?
f"https://www.stundenplan24.de/{schoolcode}/moble/mobdaten/Lehrer.xml"              # -> Klassen
f"https://www.stundenplan24.de/{schoolcode}/moble/mobdaten/PlanLe{yyyymmdd}.xml"    # Klassen
f"https://www.stundenplan24.de/{schoolcode}/vplanle/vdaten/VplanLe.xml"             # -> neu
f"https://www.stundenplan24.de/{schoolcode}/vplanle/vdaten/VplanLe{yyyymmdd}.xml"   # neu

f"https://www.stundenplan24.de/{schoolcode}/wplan/wdaten/SPlanKl_Basis.xml"         # ?
f"https://www.stundenplan24.de/{schoolcode}/mobil/mobdaten/Klassen.xml"             # -> Klassen
f"https://www.stundenplan24.de/{schoolcode}/mobil/mobdaten/PlanKl{yyyymmdd}.xml"    # Klassen
f"https://www.stundenplan24.de/{schoolcode}/vplan/vdaten/VplanKl.xml"               # -> neu
f"https://www.stundenplan24.de/{schoolcode}/vplan/vdaten/VplanKl{yyyymmdd}.xml"     # neu

f"https://www.stundenplan24.de/{schoolcode}/wplan/wdatenr/SPlanRa_Basis.xml"        # Raeume
f"https://www.stundenplan24.de/{schoolcode}/mobra/mobdaten/Raeume.xml"              # -> Klassen
f"https://www.stundenplan24.de/{schoolcode}/mobra/mobdaten/PlanRa{yyyymmdd}.xml"    # Klassen
```

### Vertretungsplan XML Baum
```
VpMobil
├── Kopf
│   ├── planart
│   ├── zeitstempel
│   ├── DatumPlan
│   ├── datei
│   ├── nativ
│   ├── woche
│   ├── tageprowoche
│   └── schulnummer
├── FreieTage
│   └── ft                  # n
└── Klassen
    └── Kl                  # n
        ├── Kurz
        ├── Hash
        ├── KlStunden
        │   └── KlSt        # n
        ├── Kurse
        │   └── Ku          # n
        │       └── KKz
        ├── Unterricht
        │   └── Ue          # n
        │       └── UeNr
        └── Pl
            └── Std         # n
                ├── St
                ├── Beginn
                ├── Ende
                ├── Fa
                ├── Ku2
                ├── Le
                ├── Ra
                ├── Nr
                └── If
```