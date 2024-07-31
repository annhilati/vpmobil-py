import requests

req = requests.get(url="http://schueler:s361o97@stundenplan24.de/10126582/mobil/mobdaten/PlanKl20240619.xml")

print(req.content)

if 4 == 2 and 4 + 5:
    pass