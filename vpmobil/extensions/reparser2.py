from vpmobil.models import VertretungsTag, KlassenVertretungsTag, LehrerVertretungsTag, RaumVertretungsTag, Lehrer, Stunde



def LehrerPerspektive(tag: VertretungsTag, /) -> LehrerVertretungsTag:

    lehrer_stunden_map: dict[str, dict[int, list[Stunde]]] = {}

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
                        if (bekannte := next([bek_stunde for bek_stunde in lehrer_stunden_map[lehrer][stunde.periode] if bek_stunde.kursnummer == stunde.kursnummer], default=None)):
                            index = lehrer_stunden_map[lehrer][stunde.periode].index(bekannte)
                            lehrer_stunden_map[lehrer][stunde.periode][index] = Stunde.new(
                                ...
                            )
                            continue # wir sind hier fertig

                        lehrer_stunden_map[lehrer][stunde.periode].append(Stunde.new(...))


    if isinstance(tag, LehrerVertretungsTag):
        lehrer_stunden_map = {lehrer.kürzel: lehrer.stunden for lehrer in tag.lehrer.values()}
    if isinstance(tag, RaumVertretungsTag):
        ... # Bitte erstmal von Klassen fertigstellen


    return LehrerVertretungsTag.new(
        datum=tag.datum,
        zeitstempel=tag.zeitstempel,
        datei=None,
        freieTage=tag.freieTage,
        zusatzInfo=tag.zusatzInfo,
        lehrer=...
    )