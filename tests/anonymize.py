from __future__ import annotations
from dataclasses import replace
from vpmobil.models import Vertretungsplan

def anonymize_vertretungsplan(plan: Vertretungsplan) -> Vertretungsplan:
    """
    Erstellt eine anonymisierte Kopie des übergebenen Vertretungsplans.
    Dabei werden Lehrer-, Klassen- und Raumkürzel systematisch ersetzt und Infotexte zensiert,
    sodass keine Rückschlüsse auf reale Personen oder echte Klassen gezogen werden können.
    """
    
    lehrer_map = {}
    klassen_map = {}
    raum_map = {}

    def map_lehrer(l: str) -> str:
        if l not in lehrer_map:
            lehrer_map[l] = f"L{len(lehrer_map) + 1}"
        return lehrer_map[l]

    def map_klasse(k: str) -> str:
        if k not in klassen_map:
            klassen_map[k] = f"K{len(klassen_map) + 1}"
        return klassen_map[k]
        
    def map_raum(r: str) -> str:
        if r not in raum_map:
            raum_map[r] = f"R{len(raum_map) + 1}"
        return raum_map[r]

    new_stunden = []
    for stunde in plan.stunden:
        new_klassen = tuple(map_klasse(k) for k in stunde.klassen)
        new_lehrer = tuple(map_lehrer(l) for l in stunde.lehrer)
        new_raeume = tuple(map_raum(r) for r in stunde.räume)
        new_info = "[ANONYMISIERT]" if stunde.info else None
        new_fachmeta = "[ANONYMISIERT]" if stunde.fachmeta else None
        
        new_stunden.append(replace(
            stunde,
            klassen=new_klassen,
            lehrer=new_lehrer,
            räume=new_raeume,
            info=new_info,
            fachmeta=new_fachmeta
        ))

    new_kurse = []
    for kurs in plan.kurse:
        new_klassen = tuple(map_klasse(k) for k in kurs.klassen)
        new_lehrer = map_lehrer(kurs.lehrer) if kurs.lehrer else None
        # Normalerweise enthält 'kürzel' das Fach. Falls hier doch spezifische Namen stehen,
        # könnte man es anpassen. Standardmäßig lassen wir das Fach stehen, damit man 
        # den Plan noch auf Funktionalität testen kann.
        
        new_kurse.append(replace(
            kurs,
            klassen=new_klassen,
            lehrer=new_lehrer
        ))

    new_aufsichten = []
    for auf in plan.aufsichten:
        new_lehrer = tuple(map_lehrer(l) for l in auf.lehrer)
        new_ort = map_raum(auf.ortinfo) if auf.ortinfo else None
        
        new_aufsichten.append(replace(
            auf,
            lehrer=new_lehrer,
            ort=new_ort
        ))
        
    new_klausuren = []
    for kl in plan.klausuren:
        new_kurse_t = tuple(map_klasse(k) for k in kl.kurse)
        new_lehrer = tuple(map_lehrer(l) for l in kl.lehrer)
        new_info = "[ANONYMISIERT]" if kl.info else None
        
        new_klausuren.append(replace(
            kl,
            kurse=new_kurse_t,
            lehrer=new_lehrer,
            info=new_info
        ))

    return replace(
        plan,
        stunden=new_stunden,
        kurse=new_kurse,
        aufsichten=new_aufsichten,
        klausuren=new_klausuren,
        zusatzinfo="[ANONYMISIERT]" if plan.zusatzinfo else None,
        dateiname="Anonymisiert.xml" if plan.dateiname else None
    )