from vpmobil import Vertretungsplan, VertretungsTag, VertretungsTagLehrer, VertretungsTagRäume, Stundenplan24Pfade
from dotenv import load_dotenv
from os import getenv
from datetime import date, datetime, time
from types import NoneType
import json

load_dotenv()

vp = Vertretungsplan(getenv("SCHULNUMMER"), getenv("NUTZER"), getenv("PASSWORT"))

def main():
    
    tag = vp.fetch(datei=Stundenplan24Pfade.Klassen)

    print(tag.datei)
    assert type(tag.datei) is str

    print(tag.datum)
    assert type(tag.datum) is date

    print(tag.zeitstempel)
    assert type(tag.zeitstempel) is datetime

    print(tag.zusatzInfo)
    assert type(tag.zusatzInfo) in [str, NoneType]

    assert type(tag.freieTage) is list and len(tag.freieTage) > 0

    print(json.dumps(tag.as_dict(), ensure_ascii=False))

    if type(tag) == VertretungsTag:
        assert type(tag.klassen) is list

        for klasse in tag.klassen:
            print(klasse)

            assert type(klasse.stunden) is dict
            if len(klasse.stunden) == 0: print("\033[31mklasse.stunden == {}")

            for periode, stunden in klasse.stunden.items():
                for stunde in stunden:
                    print(stunde)

                    assert type(stunde.geändert) is bool 
                    assert type(stunde.lehrergeändert) is bool 
                    assert type(stunde.raumgeändert) is bool 
                    assert type(stunde.klassegeändert) is bool 
                    assert type(stunde.fachgeändert) is bool 
                    assert type(stunde.ausfall) is bool 
                    assert type(stunde.beginn) is time 
                    assert type(stunde.ende) is time 
                    assert type(stunde.lehrer) is list 
                    assert type(stunde.klassen) is list and len(stunde.klassen) > 0
                    assert type(stunde.räume) is list
                    assert type(stunde.info) in [str, NoneType]
                    assert type(stunde.fach) in [str, NoneType]
                    assert type(stunde.kursnummer) is int
                    assert type(stunde.periode) is int

            assert type(klasse.kürzel)  is str

            for kurs in klasse.kurse:
                print(kurs)

                assert type(kurs.kursnummer)    is int
                assert type(kurs.kürzel)        is str
                assert type(kurs.fach)          is str
                assert type(kurs.lehrer)        is str

        assert type(tag.lehrerKrank) is list
        if len(tag.lehrerKrank) == 0: print("\033[31mtag.lehrerKrank == 0")


main()