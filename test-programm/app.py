import xml.etree.ElementTree as ET

from vpmobil import Stundenplan

stundenplan = Stundenplan(10126582, "schueler", "s361o97")

#print(stundenplan.fetch(date=20240619, browser="Edge", returntype="str"))

elementtree = stundenplan.fetch(date=20240619, browser="Edge", returntype="XML")

print(type(elementtree))