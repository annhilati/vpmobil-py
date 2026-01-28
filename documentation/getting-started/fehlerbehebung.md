# Fehlerbehebung

## Plandaten können nicht abgerufen werden

Ein Tag im Vertretungsplan kann wie [hier](vertretungsplandaten-abrufen.md) gezeigt abgerufen werden. Falls dies nicht möglich ist, erhebt vpmobil-py einen Fehler.

Je nach Art des Fehler können unterschiedliche Gründe vorliegen:

### `Unauthorized`
- Benutzername oder Passwort sind ungültig
- Der Benutzer hat keine Berechtigung um auf Pläne der angeforderten Art zuzugreifen

### `ResourceNotFound`
- Die angegebene Schulnummer existiert nicht
- Der angeforderte Tag ist nicht (mehr) verfügbar:<br>
  In der Regel stehen nur Pläne für die Tage von bis zu zwei Wochen um den aktuellen Tag zum Abrufen zur Verfügung.
- Die schulische Einrichtung verwendet eine eigene Instanz von VpMobil.<br>
  In diesem Fall ist es notwendig herauszufinden, unter welcher Domain und ggf. unter welchem Pfad die Quelldateien bereitgestellt werden. Hierfür kann Hilfe im [Bugtracker von vpmobil-py](https://github.com/annhilati/vpmobil-py/issues) in Anspruch genommen werden.
- Die Schule stellt Pläne der angeforderten Art nicht zur Verfügung

### `ModuleNotFoundError`, `NameError` oder `ImportError`

In einem solchen Fall liegt ein Problem mit der Python-Installation, der Installation von vpmobil-py oder dem Aufbau des Skripts vor. Es wird empfohlen, eine Problemanalyse mit einem LLM vorzunehmen.