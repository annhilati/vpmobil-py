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
Dieses Format wird bei `/moble/mobdaten/PlanLe{yyyymmdd}.xml`, `/mobil/mobdaten/PlanKl{yyyymmdd}.xml` und `mobra/mobdaten/PlanRa{yyyymmdd}.xml` mit den exakt gleichen Tagnamen verwendet.
```yaml
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
│   └── ft                      # n
├── Klassen
│   └── Kl                      # n     # Deklariert bei PlanLe über einen Lehrer, bei PlanRa über einen Raum
│       ├── Kurz
│       ├── Hash
│       ├── KlStunden
│       │   └── KlSt            # n
│       ├── Kurse                       # Nur bei PlanKl
│       │   └── Ku              # n
│       │       └── KKz
│       ├── Unterricht                  # nur bei PlanKl
│       │   └── Ue              # n
│       │       └── UeNr
│       ├── Pl
│       │   └── Std             # n
│       │       ├── St
│       │       ├── Beginn
│       │       ├── Ende
│       │       ├── Fa
│       │       ├── Ku2
│       │       ├── Le                  # Bezeichnet bei PlanLe eine Klasse
│       │       ├── Ra                  # Bezeichnet bei PlanRa eine Klasse
│       │       ├── Nr
│       │       └── If
│       ├── Klausuren                   # Vermutlich nur bei PlanKl
│       │   └── Klausur         # n
│       │       ├── KlJahrgang
│       │       ├── KlKurs
│       │       ├── KlKursleiter
│       │       ├── KlStunde
│       │       ├── KlBeginn
│       │       ├── KlDauer
│       │       └── KlKinfo
│       └── Aufsichten                  # Vermutlich nur bei PlanLe
│           └── Aufsicht        # n
│               ├── AuTag
│               ├── AuVorStunde
│               ├── AuUhrzeit
│               ├── AuZeit
│               └── AuOrt
└── ZusatzInfo
    └── ZiZeile
```