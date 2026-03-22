import re

StBennoGymnasium = {
    "AUFZÄHLUNGS_SEPARATOR": " ",
    "KLASSENBEZEICHNER_PATTERN": r"(?P<stufe>[1-9][0-9]?)(?P<suffix>[a-z])"

}

TolkewitzCampus = {
    "AUFZÄHLUNGS_SEPARATOR": " ",
    "KLASSENBEZEICHNER_PATTERN": r"(?P<stufe>[1-9][0-9]?)/(?P<suffix>[1-9][0-9]?)"
}

TGS6Steigerblick = {
    "KLASSENBEZEICHNER_PATTERN": r"(?P<stufe>0?[1-9][0-9]?)\s+(?P<suffix>[a-zA-Z])"
}
