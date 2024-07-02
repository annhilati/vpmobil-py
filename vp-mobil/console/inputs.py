def inputInt(prompt: str, errormsg: str = None) -> int:
    """
    Expects an input until a valid integer is specified

    prompt: A Text to be displayed in front of the input
    errormsg: A optional message, printed when the input isn't valid
    """
    while True:
        userInput = input(prompt)
        try:
            return int(userInput)
        except:
            if errormsg:
                print(errormsg)

def inputFloat(prompt: str, errormsg: str = None) -> float:#
    """
    Expects an input until a valid float is specified

    prompt: A Text to be displayed in front of the input
    errormsg: A optional message, printed when the input isn't valid
    """
    while True:
        userInput = input(prompt)
        try:
            return float(userInput)
        except:
            if errormsg:
                print(errormsg)

def inputYN(prompt: str, errormsg: str = None) -> bool:
    """
    Expects an input that matches one of many ways saying yes or no

    prompt: A Text to be displayed in front of the input
    errormsg: A optional message, printed when the input isn't valid
    """
    while True:
        userInput = input(prompt)
        if userInput in ["y", "Y", "yes", "Yes", "YES", "yES", "ja", "j", "Ja", "JA", "jA"]:
            return True
        elif userInput in ["n", "N", "no", "No", "NO", "nO", "nein", "Nein", "NO", "nEIN"]:
            return True
        else:
            if errormsg:
                print(errormsg)