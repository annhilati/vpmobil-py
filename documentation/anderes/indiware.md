---
icon: sparkle
---

# Indiware Spezifikationen

## Endpoints

```py
f"https://www.stundenplan24.de/{schoolcode}/wplan/wdaten/SPlanKl_Basis.xml"         # (Funktion unbekannt)
f"https://www.stundenplan24.de/{schoolcode}/mobil/mobdaten/Klassen.xml"             # aktueller Klassenplan
f"https://www.stundenplan24.de/{schoolcode}/mobil/mobdaten/PlanKl{yyyymmdd}.xml"    # bestimmter Klassenplan
f"https://www.stundenplan24.de/{schoolcode}/vplan/vdaten/VplanKl.xml"               # aktueller Klassenänderungsplan
f"https://www.stundenplan24.de/{schoolcode}/vplan/vdaten/VplanKl{yyyymmdd}.xml"     # bestimmter Klassenänderungsplan

f"https://www.stundenplan24.de/{schoolcode}/wplan/wdaten/SPlanLe_Basis.xml"         # (Funktion unbekannt)
f"https://www.stundenplan24.de/{schoolcode}/moble/mobdaten/Lehrer.xml"              # aktueller Lehrerplan
f"https://www.stundenplan24.de/{schoolcode}/moble/mobdaten/PlanLe{yyyymmdd}.xml"    # bestimmter Lehrerplan
f"https://www.stundenplan24.de/{schoolcode}/vplanle/vdaten/VplanLe.xml"             # aktueller Lehreränderungsplan
f"https://www.stundenplan24.de/{schoolcode}/vplanle/vdaten/VplanLe{yyyymmdd}.xml"   # bestimmter Lehreränderungsplan

f"https://www.stundenplan24.de/{schoolcode}/wplan/wdatenr/SPlanRa_Basis.xml"        # (Funktion unbekannt)
f"https://www.stundenplan24.de/{schoolcode}/mobra/mobdaten/Raeume.xml"              # aktueller Raumplan
f"https://www.stundenplan24.de/{schoolcode}/mobra/mobdaten/PlanRa{yyyymmdd}.xml"    # bestimmter Raumplan
```

## Tagesplan XML Baum

Dieses Format wird bei `/moble/mobdaten/PlanLe{yyyymmdd}.xml`, `/mobil/mobdaten/PlanKl{yyyymmdd}.xml` und `mobra/mobdaten/PlanRa{yyyymmdd}.xml` mit den exakt gleichen Tagnamen verwendet.

Tags, die mit `# n` markiert sind, können mehrfach vorkommen.

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
│   └── Kl                      # n     # Beschreibt bei PlanLe über einen Lehrer, bei PlanRa über einen Raum
│       ├── Kurz
│       ├── Hash
│       ├── KlStunden
│       │   └── KlSt            # n
│       ├── Kurse                       # Nur bei PlanKl
│       │   └── Ku              # n
│       │       └── KKz
│       ├── Unterricht                  # Nur bei PlanKl
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
│       ├── Klausuren                   # Nur bei PlanKl
│       │   └── Klausur         # n
│       │       ├── KlJahrgang
│       │       ├── KlKurs
│       │       ├── KlKursleiter
│       │       ├── KlStunde
│       │       ├── KlBeginn
│       │       ├── KlDauer
│       │       └── KlKinfo
│       └── Aufsichten                  # Nur bei PlanLe
│           └── Aufsicht        # n
│               ├── AuTag
│               ├── AuVorStunde
│               ├── AuUhrzeit
│               ├── AuZeit
│               └── AuOrt
└── ZusatzInfo
    └── ZiZeile
```
