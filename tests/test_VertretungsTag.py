from vpmobil import Vertretungsplan, Standardpfade, VertretungsTag, KlassenVertretungsTag
import dotenv, os

dotenv.load_dotenv()
vp = Vertretungsplan(os.getenv("SCHULNUMMER"), os.getenv("NUTZER"), os.getenv("PASSWORT"))

def test_fetch():
    data = vp.get(datei=Standardpfade.Klassen)

    assert type(data) == KlassenVertretungsTag