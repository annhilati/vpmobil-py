from vpmobil import Stunde, Kurs, Klasse, Lehrer, Raum
from datetime import time

Klasse. new
Lehrer. new
Raum.   new
Stunde. new
Kurs.   new


def test_stunde():
    stunde = Stunde.new(
        periode=1,
        beginn=time(8, 0),
        ende=time(9, 30),
        kursnummer=4242,
        fach="Os",
        raumgeändert=True,
        klassen=["10a"],
        lehrer=["Ah"],
        räume=["101"],
    )
    assert stunde.beginn == time(8, 0)
    assert stunde.ende == time(9, 30)
    assert stunde.räume == ["101"]