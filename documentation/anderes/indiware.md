---
icon: sparkle
---

# Indiware Spezifikationen

## Endpoints

```py
# VpMobil24 App
f"https://stundenplan24.de/{schoolcode}/mobil/mobdaten/Klassen.xml"             # aktueller Klassenplan
f"https://stundenplan24.de/{schoolcode}/mobil/mobdaten/PlanKl{yyyymmdd}.xml"    # bestimmter Klassenplan
f"https://stundenplan24.de/{schoolcode}/moble/mobdaten/Lehrer.xml"              # aktueller Lehrerplan
f"https://stundenplan24.de/{schoolcode}/moble/mobdaten/PlanLe{yyyymmdd}.xml"    # bestimmter Lehrerplan
f"https://stundenplan24.de/{schoolcode}/mobra/mobdaten/Raeume.xml"              # aktueller Raumplan
f"https://stundenplan24.de/{schoolcode}/mobra/mobdaten/PlanRa{yyyymmdd}.xml"    # bestimmter Raumplan
f"https://stundenplan24.de/{schoolcode}/mobil/mobdaten/vpinfok.txt"             # (konkrete Funktion unbekannt)

# Vertretungsplan (Monitor & PDF)
f"https://stundenplan24.de/{schoolcode}/vplan/vdaten/VplanKl.xml"               # aktueller Änderungsplan für Schüler
f"https://stundenplan24.de/{schoolcode}/vplan/vdaten/VplanKl{yyyymmdd}.xml"     # bestimmter Änderungsplan für Schüler
f"https://stundenplan24.de/{schoolcode}/vplanle/vdaten/VplanLe.xml"             # aktueller Änderungsplan für Lehrer
f"https://stundenplan24.de/{schoolcode}/vplanle/vdaten/VplanLe{yyyymmdd}.xml"   # bestimmter Änderungsplan für Lehrer

# Funktion unbekannt
f"https://stundenplan24.de/{schoolcode}/wplan/wdaten/SPlanKl_Basis.xml"
f"https://stundenplan24.de/{schoolcode}/wplan/wdaten/SPlanLe_Basis.xml"
f"https://stundenplan24.de/{schoolcode}/wplan/wdatenr/SPlanRa_Basis.xml"

```

## Tagesplan

Dieses XML-Format wird als Quellformat für die VpMobil24 App verwendet.

```yaml
<VpMobil>
├── <Kopf>
│   ├── <planart>
│   ├── <zeitstempel>                   # strptime Format: '%d.%m.%Y, %H:%M'
│   ├── <DatumPlan>                     # strptime Format: '%A, %d. %B %Y'
│   ├── <datei>
│   ├── <nativ>
│   ├── <woche>
│   ├── <tageprowoche>
│   └── <schulnummer>
├── <FreieTage>
│   └── *<ft>                           # strptime Format: '%y%m%d'
├── <Klassen>
│   └── *<Kl>                           # Beschreibt bei Typ K eine Klasse, bei Typ L einen Lehrer, bei Typ R einen Raum
│       ├── <Kurz>
│       ├── <Hash>
│       ├── <KlStunden>
│       │   └── *<KlSt>
│       │       ├ ZeitVon               # strptime Format: '%H:%M'
│       │       └ ZeitBis               # strptime Format: '%H:%M'
│       ├── <Kurse>                     # Nur bei Typ K
│       │   └── *<Ku>
│       │       └── <KKz>
│       │           └ KLe
│       ├── <Unterricht>                # Nur bei Typ K
│       │   └── *<Ue>
│       │       └── <UeNr>
│       │           ├ UeLe
│       │           ├ UeGr
│       │           └ UeFa
│       ├── <Pl>
│       │   └── *<Std>
│       │       ├── <St>
│       │       ├── <Beginn>            # strptime Format: '%H:%M'
│       │       ├── <Ende>              # strptime Format: '%H:%M'
│       │       ├── <Fa>
│       │       │   └ FaAe              # Literal: 'FaGeaendert'
│       │       ├── <Ku2>
│       │       ├── <Le>                # Bezeichnet bei Typ L eine Klasse
│       │       │   └ LeAe              # Literal: 'LeGeaendert'
│       │       ├── <Ra>                # Bezeichnet bei Typ R eine Klasse
│       │       │   └ RaAe              # Literal: 'RaGeaendert'
│       │       ├── <Nr>
│       │       └── <If>
│       ├── <Klausuren>                 # Nur bei Typ K
│       │   └── *<Klausur>
│       │       ├── <KlJahrgang>
│       │       ├── <KlKurs>
│       │       ├── <KlKursleiter>
│       │       ├── <KlStunde>
│       │       ├── <KlBeginn>
│       │       ├── <KlDauer>
│       │       └── <KlKinfo>
│       └── <Aufsichten>                # Nur bei Typ L
│           └── *<Aufsicht>
│               ├── <AuTag>
│               ├── <AuVorStunde>
│               ├── <AuUhrzeit>
│               ├── <AuZeit>
│               └── <AuOrt>
└── <ZusatzInfo>
    └── <ZiZeile>
```

## Vertretungsplan

Dieses XML-Format wird als Quellformat für Informationsmonitore und Vertretungsplan-PDFs verwendet.

```yaml
<vp>
├   <kopf>
│   ├── <datei>
│   ├── <titel>
│   ├── <schulname>
│   ├── <datum>
│   └── <kopfinfo>
│       ├── <abwesendl>
│       ├── <abwesendk>
│       ├── <aenderungl>
│       └── <aenderungk>
├── <freietage>
│   └── *<ft>                           # strptime Format: '%y%m%d'
├── <haupt>
│   └── *<aktion>
│       ├── <klasse>
│       ├── <stunde>
│       ├── <fach>
│       │   └ fageaendert
│       ├── <lehrer>
│       │   └ legeaendert
│       ├── <raum>
│       │   └ rageaendert
│       └── <info>
└── <fuss>
    └── <fusszeile>
        └── <fussinfo>
```

## vpinfok.txt

Die genaue Funktion dieser Datei im INI-Format ist unbekannt.

```yaml
[Grunddaten]
├── Nativ
├── Datum                               # strptime Format: '%d.%m.%Y'
├── Uhrzeit                             # strptime Format: '%H:%M:%S'
├── Plan1                               # strptime Format: '%Y%m%d'
├── Plan2                               # strptime Format: '%Y%m%d'
├── Plan3                               # strptime Format: '%Y%m%d'
├── Plan4                               # strptime Format: '%Y%m%d'
└── Anzahl
```