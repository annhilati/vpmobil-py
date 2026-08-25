---
icon: lucide/notebook-tabs
title: Endpoints
---

# Indiware Spezifikationen

## Endpoints

!!! info
    Nicht alle Schulen stellen alle Endpunkte zur Verfügung.

```py
# VpMobil24 App
f"https://stundenplan24.de/{schulnummer}/mobil/mobdaten/Klassen.xml"             # zuletzt geänderter Klassenplan
f"https://stundenplan24.de/{schulnummer}/mobil/mobdaten/PlanKl{yyyymmdd}.xml"    # datierter Klassenplan
f"https://stundenplan24.de/{schulnummer}/moble/mobdaten/Lehrer.xml"              # zuletzt geänderter Lehrerplan
f"https://stundenplan24.de/{schulnummer}/moble/mobdaten/PlanLe{yyyymmdd}.xml"    # datierter Lehrerplan
f"https://stundenplan24.de/{schulnummer}/mobra/mobdaten/Raeume.xml"              # zuletzt geänderter Raumplan
f"https://stundenplan24.de/{schulnummer}/mobra/mobdaten/PlanRa{yyyymmdd}.xml"    # datierter Raumplan
f"https://stundenplan24.de/{schulnummer}/mobil/mobdaten/vpinfok.txt"             # (konkrete Funktion unbekannt)

# Vertretungsplan (Monitor & PDF)
f"https://stundenplan24.de/{schulnummer}/vplan/vdaten/VplanKl.xml"               # zuletzt geänderter Änderungsplan für Schüler
f"https://stundenplan24.de/{schulnummer}/vplan/vdaten/VplanKl{yyyymmdd}.xml"     # datierter Änderungsplan für Schüler
f"https://stundenplan24.de/{schulnummer}/vplanle/vdaten/VplanLe.xml"             # zuletzt geänderter Änderungsplan für Lehrer
f"https://stundenplan24.de/{schulnummer}/vplanle/vdaten/VplanLe{yyyymmdd}.xml"   # datierter Änderungsplan für Lehrer

# Funktion unbekannt
f"https://stundenplan24.de/{schulnummer}/wplan/wdaten/SPlanKl_Basis.xml"
f"https://stundenplan24.de/{schulnummer}/wplan/wdaten/SPlanLe_Basis.xml"
f"https://stundenplan24.de/{schulnummer}/wplan/wdatenr/SPlanRa_Basis.xml"
f"https://stundenplan24.de/{schulnummer}/wplan/wdatenk/SPlanKl_Sw{schulwoche}.xml"
f"https://stundenplan24.de/{schulnummer}/wplan/wdatenk/WPlanKl{yyyymmdd}.xml"

f"https://stundenplan24.de/{schulnummer}/splan/sdaten/splank.xml"               # Stundenpläne der Klassen

```

## Vertretungsplan

Dieses XML-Format wird als Quellformat für einzelne Tage in der VpMobil24 App verwendet.

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

## Vertretungsplan (nur Änderungen)

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

## Stundenplan

```yaml
<splan>
├── <Kopf>
│   ├── <PlanArt>
│   ├── <zeitstempel>
│   ├── <datei>
│   ├── <gueltigab>
│   ├── <schulname>
│   ├── <schulort>
│   ├── <upname>
│   ├── <upmodul>
│   └── <upversion>
├── <FreieTage>
│   └── *<ft>                           # strptime Format: '%y%m%d'
├── <Kalenderwochen>
│   └─── *<Kw>
│       ├ KwNr
│       ├ KwDatumVon
│       ├ KwDatumBis
│       └ KwWoche
├── <Schulwochen>
│   └─── *<Sw>
│       ├ SwKw
│       └ SwDatum
└── <Klassen>
    └── *<Kl>
        ├── <Kurz>
        ├── <Stunden>
        │   └── *<St>
        │       ├ StZeit
        │       └ StZeitBis
        ├── <Sperrungen>
        │   └── *<Sp>
        │       ├ SpTg
        │       └ SpSt
        └── <Pl>
            └── *<Std>
                ├── <PlSw>
                ├── <PlTg>
                ├── <PlSt>
                ├── <PlFa>
                ├── <PlKl>
                ├── <PlLe>
                ├── <PlRa>
                └── <PlWo>
```

## vpinfok.txt

Diese Datei enthält vermutlich Metadaten, die von der VpMobil24-App genutzt werden, um zu wissen, welche Pläne abzurufen sind.

```yaml
[Grunddaten]
├── Nativ
├── Datum                               # strptime Format: '%d.%m.%Y', Datum der letzten Aktualisierung
├── Uhrzeit                             # strptime Format: '%H:%M:%S', Uhrzeit der letzten Aktualisierung
├── Plan1                               # strptime Format: '%Y%m%d'
├── Plan2                               # strptime Format: '%Y%m%d'
├── Plan3                               # strptime Format: '%Y%m%d'
├── Plan4                               # strptime Format: '%Y%m%d'
└── Anzahl
```