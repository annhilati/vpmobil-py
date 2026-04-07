from vpmobil import Stunde, Kurs, Klasse, Lehrer, Raum
from datetime import time

if 2 == 3:
    Klasse ()
    Lehrer ()
    Raum   ()
    Stunde ()
    Kurs   ()


def test_stunde():
    stunde = Stunde(
        periode=1,
        beginn=time(8, 0),
        ende=time(9, 30),
        kursnummer=4242,
        fach="Os",
        raumänderung=True,
        klassen=["10a"],
        lehrer=["Ah"],
        räume=["101"],
    )
    assert stunde.beginn == time(8, 0)
    assert stunde.ende == time(9, 30)
    assert stunde.räume == ["101"]