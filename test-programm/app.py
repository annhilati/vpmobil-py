import xml.etree.ElementTree as ET
from vpmobil import Stundenplan

stundenplan = Stundenplan(10126582, "schueler", "s361o97")

#tag = stundenplan.fetch(date=20240619)
tag = stundenplan.fetch(date=20240215)

print(tag.getxml())