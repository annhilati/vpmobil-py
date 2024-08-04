<h1 align="center">vpmobil-py</h1>
<p align="center">
  <a href="#"><img alt="CodeSnap" height="150" src="https://github.com/user-attachments/assets/27152a55-aa5e-4d80-bbd3-7dc64b35e77e"></a>
  <br>
  <a href="https://pypi.org/project/vpmobil">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/v/vpmobil?style=for-the-badge&logo=pypi&logoColor=white&label=Version&color=5865F2"></a>
  <a href="https://pypi.org/project/vpmobil/">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dw/vpmobil?style=for-the-badge&logo=pypi&logoColor=white&label=Downloads&color=5865F2"></a>
  <br>
  <a href="https://annhilati.gitbook.io/vpmobil">
    <img alt="Static Badge" src="https://img.shields.io/badge/Gitbook-Documentation?style=for-the-badge&logo=gitbook&logoColor=white&label=Documentation&color=23A55A"></a>
  <a href="https://github.com/annhilati/vpmobil-py?tab=GPL-3.0-1-ov-file">
    <img alt="GitHub License" src="https://img.shields.io/github/license/annhilati/vpmobil-py?style=for-the-badge&label=Lizenz&color=F23F42"></a>
  <br>
  <a href="https://github.com/annhilati/vpmobil-py">
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/annhilati/vpmobil-py?style=for-the-badge&logo=github&label=Letzter%20Commit&color=23A55A"></a>  

```python
from vpmobil import Vertretungsplan

vp = Vertretungsplan(39563772, "schueler", "j39jjs6")

tag = vp.fetch(20240619)
klasse = tag.klasse("9b")
stunden = klasse.stunden()

for stunde in stunden:
  print(f"{stunde.nr}: {stunde.fach} bei {stunde.lehrer} in {stunde.raum}")
```

  <p align="center">Because Indiware only distributes substitution plan modules in Germany and the vast majority of users are therefore German, the package and the wiki are formulated in German</p>
</p>

<h2>Features</h2>
<h6>Dies ist eine grobe Übersicht über die Features und ist nicht unbedingt aktuell</h6>
<h3>Symbole</h4>
<ul>
  <li>Vertretungsplan
    <ul>
      <li>.fetch()</li>
      <li>.fetchall()</li>
    </ul>
  </li>
  <li>VpDay</li>
    <ul>
      <li>.datum</li>
      <li>.wochentag</li>
      <li>.zusatzInfo</li>
      <li>.zeitstempel</li>
      <li>.datei</li>
      <li>.klassen()</li>
      <li>.freieTage()</li>
      <li>.lehrerKrank</li>
      <li>.saveasfile()</li>
      <li>:xml</li>
    </ul>
  <li>Klasse</li>
    <ul>
      <li>.kürzel</li>
      <li>.stundenInPeriode()</li>
      <li>.stunden()</li>
      <li>:xml</li>
    </ul>
  <li>Stunde</li>
    <ul>
      <li>.nr</li>
      <li>.beginn()</li>
      <li>.ende</li>
      <li>.anders</li>
      <li>.besonders</li>
      <li>.ausfall</li>
      <li>.fach</li>
      <li>.lehrer</li>
      <li>.raum</li>
      <li>.info()</li>
      <li>.kursnummer</li>
      <li>:xml</li>
    </ul>
  <li>Kurs (WiP)</li>
    <ul>
      <li>.lehrer</li>
      <li>.fach</li>
      <li>.zusatz</li>
      <li>.kursnummer</li>
    </ul>
  <li>VpMobil</li>
    <ul>
      <li>.getxml()</li>
      <li>.parsefromfile()</li>
      <li>.FetchingError</li>
      <li>.InvalidCredentialsError</li>
      <li>.XMLParsingError</li>
      <li>.XMLNotFound</li>
    </ul>
  </li>
</ul>



<h3 align="center"> DISCLAIMER </h3>
<p align="center">
  Das Paket und seine zugehörigen Dienste und Projekte sind eigenständig und stehen in keiner Verbindung zu Indiware, der VpMobil24 App oder stundenplan24.de. Die Nutzung obliegt der Verantwortung des Nutzers. Die   Entwickler übernimmt keine Haftung für Schäden, die durch die Nutzung der App entstehen.
</p>

<!-- https://annhilati.gitbook.io/db/pypi-upload>
