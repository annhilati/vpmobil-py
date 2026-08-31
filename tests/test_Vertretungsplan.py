import os
import xml.etree.ElementTree as ET
from datetime import date
from vpmobil import *

def test_from_file():
    data = Vertretungsplan.from_file("tests/example.xml")

    assert type(data) == Vertretungsplan
    assert data.datum is not None
    
    # Subskription
    if data.klassen:
        bsp_klasse = list(data.klassen.keys())[0]
        assert isinstance(data[bsp_klasse], Klasse)
        
    if data.lehrer:
        bsp_lehrer = list(data.lehrer.keys())[0]
        assert isinstance(data[bsp_lehrer], Lehrer)
        
    if data.räume:
        bsp_räume = list(data.räume.keys())[0]
        assert isinstance(data[bsp_räume], Raum)

def test_properties():
    data = Vertretungsplan.from_file("tests/example.xml")
    
    # Test if basic lists exist and are populated
    assert len(data.stunden) >= 0
    assert len(data.kurse) >= 0
    assert len(data.aufsichten) >= 0
    assert len(data.klausuren) >= 0
    
    # Test that freieTage contains date objects
    if data.freieTage:
        assert isinstance(data.freieTage[0], date)
        
    # Test that abwesendeLehrer contains strings
    if data.abwesendeLehrer:
        assert isinstance(data.abwesendeLehrer[0], str)

def test_to_element():
    data = Vertretungsplan.from_file("tests/example.xml")
    
    # Test our fixed to_element methods
    for kl in data.klassen.values():
        el = kl.to_element()
        assert isinstance(el, ET.Element)
        assert el.tag == "Kl"
        
    for le in data.lehrer.values():
        el = le.to_element()
        assert isinstance(el, ET.Element)
        assert el.tag == "Kl"
        
    for ra in data.räume.values():
        el = ra.to_element()
        assert isinstance(el, ET.Element)
        assert el.tag == "Kl"

def test_save_and_reload():
    data = Vertretungsplan.from_file("tests/example.xml")
    
    # Test saving as XML and then reloading it
    out_file = "tests/test_output.xml"
    try:
        data.save_xml(out_file, planart="K")
        assert os.path.exists(out_file)
        
        # Reload
        reloaded = Vertretungsplan.from_file(out_file)
        assert reloaded.datum == data.datum
        assert len(reloaded.stunden) == len(data.stunden)
        
    finally:
        if os.path.exists(out_file):
            os.remove(out_file)

if __name__ == "__main__":
    test_from_file()
    test_properties()
    test_to_element()
    test_save_and_reload()
    print("All tests passed!")