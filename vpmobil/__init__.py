"""
A python module for interacting with a stundenplan24.de substitution plan
"""

from .Vertretungsplan import Vertretungsplan
from .VpDay import VpDay, Stunde

__all__ = ['Vertretungsplan', "VpDay", "Stunde"]
    # Enthält alle Symbole, die bei "from vpmobil import" verfügbar sind
    # Enthält alle Symbole, die bei "from vpmobil import *" importiert werden