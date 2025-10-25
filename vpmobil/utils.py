from datetime import date, timedelta
import string
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
import re

from vpmobil import config

def prettyxml(object: ET.Element | ET.ElementTree) -> str:
    if isinstance(object, ET.ElementTree):
        element = object.getroot()
    elif isinstance(object, ET.Element):
        element = object
    else:
        element = object
    
    string = ET.tostring(element, 'utf-8')
    reparsed = MD.parseString(string)
    return reparsed.toprettyxml(indent="\t")


def date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


import re
import string
from typing import List

def parse_aufzählung(
    s: str,
    separator: str = config.AUFZÄHLUNGS_SEPARATOR,
    parse_hyphen: bool = config.BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN,
    class_pattern: re.Pattern = config.KLASSEN_BEZEICHNER_PATTERN,
) -> List[str]:
    """Parst Klassenangaben wie '5a', '5a-5c', '5a,5b,6a-7a', '9b-10c'
    oder '5/1-5/3' zu einer Liste von Strings, basierend auf dem konfigurierten Pattern."""

    if not s:
        return []

    parts = [p.strip() for p in s.split(separator) if p.strip()]

    if not parse_hyphen:
        return parts

    result: list[str] = []

    for part in parts:
        if "-" not in part:
            result.append(part)
            continue

        start_raw, end_raw = part.split("-", 1)
        start_match = class_pattern.fullmatch(start_raw.strip())
        end_match = class_pattern.fullmatch(end_raw.strip())

        if not (start_match and end_match):
            # Fallback: unverständlicher Bereich, unverändert übernehmen
            result.append(part)
            continue

        s_stufe, s_suffix = start_match["stufe"], start_match["suffix"]
        e_stufe, e_suffix = end_match["stufe"], end_match["suffix"]

        # Unterscheide Zahlensuffix (z. B. 5/1–5/3) vs. Buchstabensuffix (z. B. 5a–5c)
        if s_suffix.isdigit() and e_suffix.isdigit():
            if s_stufe == e_stufe:
                for i in range(int(s_suffix), int(e_suffix) + 1):
                    result.append(f"{s_stufe}/{i}")
            else:
                for n in range(int(s_stufe), int(e_stufe) + 1):
                    result.append(f"{n}/{s_suffix}")  # fallback bei ungleicher stufe
            continue

        if s_suffix.isalpha() and e_suffix.isalpha():
            letters = list(string.ascii_lowercase)
            start_i = letters.index(s_suffix)
            end_i = letters.index(e_suffix)
            if s_stufe == e_stufe:
                for c in letters[start_i:end_i + 1]:
                    result.append(f"{s_stufe}{c}")
            else:
                for n in range(int(s_stufe), int(e_stufe) + 1):
                    for c in letters[start_i:end_i + 1]:
                        result.append(f"{n}{c}")
            continue

        # Wenn gemischt oder nicht eindeutig, einfach übernehmen
        result.append(part)

    return result

print(parse_aufzählung("5a-10c, 5/1-5/4"))