from vpmobil.models import VertretungsTag, KlassenVertretungsTag, LehrerVertretungsTag, RaumVertretungsTag, Lehrer, Stunde, Klasse, Raum


type VertretungsTagType = KlassenVertretungsTag | RaumVertretungsTag | LehrerVertretungsTag
type KlasseLikeType = Klasse | Lehrer | Raum

def LehrerPerspektive(tag: VertretungsTag, /) -> LehrerVertretungsTag:

    lehrer_stunden_map: dict[str, dict[int, list[Stunde]]] = {} # Wir benutzen das, weil KlasseLikeType Objekte praktisch immutable sind

    if isinstance(tag, KlassenVertretungsTag):
        for klasse in tag.klassen.values():
            for periode in klasse.stunden.values():
                for stunde in periode:  
                    for lehrer in stunde.lehrer:

                        if lehrer not in lehrer_stunden_map:
                            lehrer_stunden_map[lehrer] = {}
                        if stunde.periode not in lehrer_stunden_map[lehrer]:
                            lehrer_stunden_map[lehrer][stunde.periode] = []

                        # Kriterien gerne nochmal konkretisieren
                        if (bekannte := next((
                            parallelstunde for parallelstunde in lehrer_stunden_map[lehrer][stunde.periode]
                            if parallelstunde.kursnummer == stunde.kursnummer
                            or stunde.kursnummer is None and stunde.räume == parallelstunde.räume 
                        ), None)):
                            index = lehrer_stunden_map[lehrer][stunde.periode].index(bekannte)
                            lehrer_stunden_map[lehrer][stunde.periode][index] = Stunde.new(
                                planart="L",
                                periode=stunde.periode,
                                beginn=stunde.beginn or bekannte.beginn,
                                ende=stunde.ende or bekannte.ende,
                                kursnummer = stunde.kursnummer,
                                fach = stunde.fach or stunde.fach,
                                fachmeta = stunde.fachmeta or stunde.fachmeta,
                                fachgeändert = stunde.fachgeändert,
                                lehrer = list(set(stunde.lehrer) | set(bekannte.lehrer)),
                                räume = list(set(stunde.räume) | set(bekannte.räume)),
                                klassen= list(set(stunde.klassen) | set(bekannte.klassen)),
                                lehrergeändert = stunde.lehrergeändert,
                                raumgeändert = stunde.raumgeändert,
                                klassegeändert = stunde.klassegeändert,
                                info = stunde.info or stunde.info
                            )
                        else:
                            lehrer_stunden_map[lehrer][stunde.periode].append(Stunde.new(
                                planart="L",
                                periode=stunde.periode,
                                beginn=stunde.beginn,
                                ende=stunde.ende,
                                kursnummer = stunde.kursnummer,
                                fach = stunde.fach,
                                fachmeta = stunde.fachmeta,
                                fachgeändert = stunde.fachgeändert,
                                lehrer = stunde.lehrer,
                                räume = stunde.räume,
                                klassen= stunde.klassen,
                                lehrergeändert = stunde.lehrergeändert,
                                raumgeändert = stunde.raumgeändert,
                                klassegeändert = stunde.klassegeändert,
                                info = stunde.info
                            ))


    if isinstance(tag, LehrerVertretungsTag):
        return tag
    if isinstance(tag, RaumVertretungsTag):
        ... # Bitte erstmal von Klassen fertigstellen


    return LehrerVertretungsTag.new(
        datum=tag.datum,
        zeitstempel=tag.zeitstempel,
        datei=None,
        freieTage=tag.freieTage,
        zusatzInfo=tag.zusatzInfo,
        lehrer=[Lehrer.new(
            kürzel=kürzel,
            stunden=[stunde for period_list in lehrer_stunden_map[kürzel].values() for stunde in period_list]
        ) for kürzel in lehrer_stunden_map.keys()]
    )