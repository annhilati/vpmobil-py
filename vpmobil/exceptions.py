import requests

# ╭────────────────────────────────────────────────────────────────────────────────╮
# │                                FetchingError                                   │ 
# ╰────────────────────────────────────────────────────────────────────────────────╯

class FetchingError(Exception):
    "Wenn die angeforderten Daten nicht abgerufen werden können"
    def __init__(self, message: str, response: requests.Response = None):
        self.message = message
        self.response = response

    def __str__(self):
        return f"{self.message} ({self.response})"

class InvalidCredentialsError(FetchingError):
    ...

# ╭────────────────────────────────────────────────────────────────────────────────╮
# │                               XMLParsingError                                  │ 
# ╰────────────────────────────────────────────────────────────────────────────────╯

class XMLParsingError(Exception):
    "Wenn XML-Daten nicht richtig geparst werden können"
    ...