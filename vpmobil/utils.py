from enum import StrEnum

from vpmobil.models import *
from vpmobil import config

class Stundenplan24Pfade(StrEnum):
    """Enumerator mit den Pfaden für Vertretungsplanquelldateien, wie sie auf `stundenplan24.de` verwendet werden.<br>
    
    Pfade enthalten die Platzhalter `{schulnummer}`, `&Y`, `%m` und `%d`.
    """
    Klassen = "{schulnummer}/mobil/mobdaten/Klassen.xml"
    PlanKl  = "{schulnummer}/mobil/mobdaten/PlanKl%Y%m%d.xml"
    Lehrer  = "{schulnummer}/moble/mobdaten/Lehrer.xml"
    PlanLe  = "{schulnummer}/moble/mobdaten/PlanLe%Y%m%d.xml"
    Raeume  = "{schulnummer}/mobra/mobdaten/Raeume.xml"
    PlanRa  = "{schulnummer}/mobra/mobdaten/PlanRa%Y%m%d.xml"

VertretungsTagType = VertretungsTag | VertretungsTagRäume | VertretungsTagLehrer
KlasseLikeType = Klasse | Lehrer | Raum

# def parse_klassen(s: str) -> list[str]:
#     """Parst Klassenangaben wie '5a', '5a-5c', '5a,5b,6a-7c' zu einer Liste von Klassen."""
#     result: list[str] = []
#     if not s:
#         return result

#     parts = [p.strip() for p in s.split(config.SEPARATOR) if p.strip()]
#     for part in parts:
#         if "-" not in part:
#             result.append(part)
#             continue

#         # Bereich mit gleicher Zahl (z. B. 5a-5c oder 5a-c)
#         m_same = re.fullmatch(r"(\d+)([a-z])-(?:\1)?([a-z])", part)
#         if m_same:
#             num = int(m_same.group(1))
#             start, end = m_same.group(2), m_same.group(3)
#             for c in letters[letters.index(start): letters.index(end) + 1]:
#                 result.append(f"{num}{c}")
#             continue

#         # Bereich mit gleicher Buchstabenposition (z. B. 5a-10a)
#         m_letter = re.fullmatch(r"(\d+)([a-z])-(\d+)\2", part)
#         if m_letter:
#             start_n, letter, end_n = int(m_letter[1]), m_letter[2], int(m_letter[3])
#             for n in range(start_n, end_n + 1):
#                 result.append(f"{n}{letter}")
#             continue

#         # alles andere ist ungültig
#         raise ValueError(f"Ungültiger Klassenbereich: {part}")

#     return result