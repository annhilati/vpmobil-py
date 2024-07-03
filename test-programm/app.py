import xml.etree.ElementTree as ET
from vpmobil import Stundenplan

stundenplan = Stundenplan(10126582, "schueler", "s361o97")

zuCheckenderTag = stundenplan.fetch(date=20240619)

print(zuCheckenderTag.getxml("str"))