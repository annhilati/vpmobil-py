import datetime

def log(text: str) -> None:
    """
    Prints a Text in the console combined with a timestamp, e.g.:
    [11:45:33] This is a custom setable message
    """
    return print("[" + datetime.datetime.now().strftime("%H:%M:%S") + "] " + text)