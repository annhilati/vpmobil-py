from vpmobil import Parser

def test_update_parser():
    p = Parser(BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN=False)
    
    p2 = p.clone(AUFZÄHLUNGS_TRENNZEICHEN=", ")
    
    assert p2.BINDESTRICHE_ALS_BEREICHE_INTERPRETIEREN == False # in ~.clone() nicht explizit gesetzte Werte bleiben unverändert
    assert p2.AUFZÄHLUNGS_TRENNZEICHEN == ", " # explizit in ~.clone() gesetzte Werte werden übernommen