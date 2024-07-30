import requests

req = requests.get("http://schueler:s361o97@stundenplan24.de/10126582/mobil/mobdaten/PlanKl20240619.xml")

print(req.content)