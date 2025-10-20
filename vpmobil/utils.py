from datetime import date, timedelta
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
import re
from string import ascii_letters as letters

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

def parse_aufzählung(s: str, separator: str, parse_hyphen: bool) -> list[str]:
    """Parst Klassenangaben wie '5a', '5a-5c', '5a,5b,6a-7a' zu einer Liste von Strings."""

    # - Gemischte Klassen (5a-10c) wieder hinzufügen
    # - Prüfen, ob Leerzeichen zwischen den - sein dürfen. Im zweifelsfall alle Whitespaces entfernen

    result: list[str] = []
    if not s:
        return result
    parts = [p.strip() for p in s.split(separator) if p.strip()]
    for part in parts:
        if "-" not in part or parse_hyphen is False:
            result.append(part)
            continue
        # Bereich mit gleicher Zahl (z. B. 5a-5c oder 5a-c)
        m_same = re.fullmatch(r"(\d+)([a-z])-(?:\1)?([a-z])", part)
        if m_same:
            num = int(m_same.group(1))
            start, end = m_same.group(2), m_same.group(3)
            for c in letters[letters.index(start): letters.index(end) + 1]:
                result.append(f"{num}{c}")
            continue
        # Bereich mit gleicher Buchstabenposition (z. B. 5a-10a)
        m_letter = re.fullmatch(r"(\d+)([a-z])-(\d+)\2", part)
        if m_letter:
            start_n, letter, end_n = int(m_letter[1]), m_letter[2], int(m_letter[3])
            for n in range(start_n, end_n + 1):
                result.append(f"{n}{letter}")
            continue
        # alles andere ist ungültig
        raise ValueError(f"Ungültiger Klassenbereich: {part}")
    return result