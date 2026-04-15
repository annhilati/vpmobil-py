---
title: Einschränkungen
---

# Einschränkungen

##  Mangel an Information bei perspektivischer Auswertung

#### Zusammenfassung
Wenn Stunden aus einer anderen Perspektive ausgewertet werden sollen, als die Quelldaten, fehlen die Stunden, deren Aspekt
korrespondierend zur Auswertungsperspektive abgändert wurde. Die Stunde steht aus der Perspektive nicht als entfallend da,
sondern feht schlichtweg.

**Beispiel:**

In den Quelldaten besitzt eine Klasse eine Stunde:

```yaml
klassen:
    10a:
        stunden:
            1:
            - klassen: ["10a"]
              lehrer: ["Herr Neu"]
              lehreränderung: true
              ...
        ...
```

Die Lehrer der Stunde wurden geändert, und sind nun `["Herr Neu"]`. Normalerweise hält `["Herr Normal"]` die Stunde, aber das ist aus den Daten nicht ersichtlich. Deswegen wird in der Perspektive `lehrer/Herr Normal` diese Stunde nicht als entfallend angeführt, sondern sie fehlt einfach.

## Auswirkungen auf vpmobil-py

- Lehrer, Räume und Klassen werden nicht geleert, falls eine Stunde ausfällt, um die Referenzen, die es gelegentlich noch gibt zu erhalten (z.B. bei Selbstaufgaben, wenn zwar eine Lehrer und ein Fach, aber kein Raum angegeben ist)