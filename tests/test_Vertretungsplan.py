from vpmobil import *
import dotenv, os

dotenv.load_dotenv()
vp = VertretungsplanZugang(os.getenv("SCHULNUMMER"), os.getenv("NUTZER"), os.getenv("PASSWORT"))

def test_fetch():
    data = vp.get(datei=Standardpfade.Klassen)

    assert type(data) == Vertretungsplan
    
    # Subskription
    bsp_klasse = list(data.klassen.keys())[0]
    assert isinstance(data[bsp_klasse], Klasse)
    bsp_lehrer = list(data.lehrer.keys())[0]
    assert isinstance(data[bsp_lehrer], Lehrer)
    bsp_räume = list(data.räume.keys())[0]
    assert isinstance(data[bsp_räume], Raum)
                
if __name__ == "__main__":
    test_fetch()