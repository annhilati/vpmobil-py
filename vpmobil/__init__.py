"""
A python package for interacting with a stundenplan24.de substitution plan
"""

from .vertretungsplan import Vertretungsplan
from .vpDay import VpDay
#from .testing import Vertretungsplan, vpDay

__all__ = ['Vertretungsplan', "VpDay"]
