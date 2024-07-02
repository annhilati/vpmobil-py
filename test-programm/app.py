import xml.etree.ElementTree as ET
from vpmobil import Stundenplan, vpDay

stundenplan = Stundenplan(10126582, "schueler", "s361o97")

vday = stundenplan.fetch(date=20240619, browser="Edge")

print(vday.out(returnformat="ElementTree"))