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


def parse_aufzählung(s: str, separator: str = config.SEPARATOR, parse_hyphen: bool = config.INTERPRET_HYPHEN_AS_RANGE) -> list[str]:
    """Parst Klassenangaben wie '5a', '5a-5c', '5a,5b,6a-7a', '9b-10c' zu einer Liste von Strings."""

    if not s:
        return []

    letters = list(string.ascii_lowercase)
    parts = [p.strip() for p in s.split(separator) if p.strip()]

    if not parse_hyphen:
        return parts

    result: list[str] = []
    for part in parts:
        if "-" in part:
            
            # Bereich mit gleicher Zahl (z. B. 5a-5c oder 5a-c)
            if m_same := re.fullmatch(r"(\d+)([a-z])-(?:\1)?([a-z])", part):
                num = int(m_same.group(1))
                start, end = m_same.group(2), m_same.group(3)
                for c in letters[letters.index(start): letters.index(end) + 1]:
                    result.append(f"{num}{c}")
                continue

            # Bereich mit gleicher Buchstabenposition (z. B. 5a-10a)
            if m_letter := re.fullmatch(r"(\d+)([a-z])-(\d+)\2", part):
                start_n, letter, end_n = int(m_letter[1]), m_letter[2], int(m_letter[3])
                for n in range(start_n, end_n + 1):
                    result.append(f"{n}{letter}")
                continue

            # Gemischter Bereich (z. B. 9b-10c)
            if m_mixed := re.fullmatch(r"(\d+)([a-z])-(\d+)([a-z])", part):
                start_n, start_l, end_n, end_l = int(m_mixed[1]), m_mixed[2], int(m_mixed[3]), m_mixed[4]
                start_li = letters.index(start_l)
                end_li = letters.index(end_l)
                for n in range(start_n, end_n + 1):
                    for li in range(start_li, end_li + 1):
                        result.append(f"{n}{letters[li]}")
                continue

        result.append(part)

    return result