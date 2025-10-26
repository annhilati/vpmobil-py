import re

StBennoGymnasium = {
    "AUFZÄHLUNGS_SEPARATOR": " ",
    "KLASSENBEZEICHNER_PATTERN": re.compile(r"(?P<stufe>[1-9][0-9]?)(?P<suffix>[a-z])")

}

TolkewitzCampus = {
    "AUFZÄHLUNGS_SEPARATOR": " ",
    "KLASSENBEZEICHNER_PATTERN": re.compile(r"(?P<stufe>[1-9][0-9]?)/(?P<suffix>[1-9][0-9]?)")

}