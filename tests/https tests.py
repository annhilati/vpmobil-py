import requests

datei = "PlanKl20240805.xml"
#req = requests.get(url=f"http://schueler:s361o97@stundenplan24.de/10126582/mobil/mobdaten/{datei}") # ok
    # 200
#req = requests.get(url=f"http://atze:s361o97@stundenplan24.de/10126582/mobil/mobdaten/{datei}") # !benutzer
    # 401
#req = requests.get(url=f"http://schueler:ssgdvgd@stundenplan24.de/10126582/mobil/mobdaten/{datei}") # !passwort
    # 401
#req = requests.get(url=f"http://schueler:s361o97@stundenplan24.de/99926582/mobil/mobdaten/{datei}") # !schulnummer
    # 404
req = requests.get(url=f"http://schueler:s361o97@stundenplan24.de/10126582/mobil/mobdaten/PlanKl20000101") # !datei vorhanden
    # 404

print(req.content)
print(req.status_code)