<h1 align="center">vpmobil-py</h1>
<h6 align="center">Das bislang mächtigste Auswertungstool für Indiware-Vertretungspläne</h6>
<p align="center">
  <code>pip install vpmobil</code>
  <br>
  <br>
  <a href="https://pypi.org/project/vpmobil">
    <img alt="PyPI Version" src="https://img.shields.io/pypi/v/vpmobil?style=for-the-badge&logo=pypi&logoColor=white&label=Version&color=5865F2"></a>
  <a href="https://pypi.org/project/vpmobil/">
    <img alt="PyPI Downloads" src="https://img.shields.io/pypi/dw/vpmobil?style=for-the-badge&logo=pypi&logoColor=white&label=Downloads&color=5865F2"></a>
  <br>
  <a href="https://annhilati.github.io/vpmobil-py">
    <img alt="Dokumentation" src="https://img.shields.io/badge/GH%20Pages-Dokumentation?style=for-the-badge&logo=gitbook&logoColor=white&label=Dokumentation&color=23A55A"></a>
  <a href="https://github.com/annhilati/vpmobil-py?tab=EUPL-1.2-1-ov-file">
    <img alt="GitHub License" src="https://img.shields.io/github/license/annhilati/vpmobil-py?style=for-the-badge&label=Lizenz&color=F23F42"></a>
  <br>
  <a href="https://github.com/annhilati/vpmobil-py">
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/annhilati/vpmobil-py?style=for-the-badge&logo=github&label=Letzter%20Commit&color=23A55A"></a>  

```python
from vpmobil import Vertretungsplan
from datetime import date

vp = Vertretungsplan(10000000, "schueler", "password")

tag = vp.fetch(date(2025, 11, 11))
klasse = tag.klassen["9b"]

for periode, stunden in klasse.stunden.items():
    for stunde in stunden:
        print(f"{periode} | {stunde.fach} bei {stunde.lehrer}")
```

> [!NOTE]
> Because Indiware only distributes substitution plan modules in Germany and the vast majority of users are therefore German, most of the package's functions and classes, their docstrings and the wiki are phrased in German.

## Features

- ⬇️ **Fetching:** Vertretungspläne flexibel aus beliebigen Quellen abrufen und einlesen
- 📦 **Objektorientiert:** Strukturierte Klassen zur typisierten Repräsentation aller Planinhalte
- 🌌 **Feature-Complete:** Sämtliche im Alltag relevanten Informationen werden vollständig abgebildet
- 🔧 **Konfiguration:** Eigenheiten der Vertretungsplaner können bei der Auswertung berücksichtig werden 
- ⚙️ **Kompatibilität:** Export der Daten in beliebige Key-Value-Formate wie JSON oder YAML
- 👁️ **Perspektivisch:** Auswertung von Plänen aus Perspektive von Klassen, Lehrern und Räumen
- 🧪 **Genese:** Generierung von Quelldateien können aus Klarwerten
- ➕ **Weitere Funktionen**: Parsen von PDFs, die von Indiware-Software erstellt werden


<h3 align="center"> DISCLAIMER </h3>
<p align="center">
  Das Paket und seine zugehörigen Dienste und Projekte sind eigenständig und stehen in keiner Verbindung zu Indiware, der VpMobil24 App oder stundenplan24.de. Die Nutzung obliegt der Verantwortung des Nutzers. Die Entwickler übernehmen keine Haftung für Schäden, die durch die Nutzung entstehen.
</p>
