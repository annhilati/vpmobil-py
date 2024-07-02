import selenium
import selenium.webdriver
import selenium.webdriver.common.by
import chromedriver_autoinstaller
import time

class Stundenplan():
    """
    Refers to a specific account on a specific VpMobil-Stundenplan
    """
    def __init__(self, schulnummer: int, benutzername: str, passwort: str):
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort
        #self.visiblewindow = False # TODO

    def fetch(self, date: int, browser: str = "Chrome"):
        """
        Prints the entire information of a specific day as XML

        - Available browsers: "Chrome", "Edge", "Firefox", "Safari"
        """
        chromedriver_autoinstaller.install()

        match browser:
            case "Chrome":
                driver = selenium.webdriver.Chrome()
            case "Edge":
                driver = selenium.webdriver.Edge()
            case "Firefox":
                driver = selenium.webdriver.Firefox()
            case "Safari":
                driver = selenium.webdriver.Safari()

        link = f"http://{self.benutzername}:{self.passwort}@stundenplan24.de/{self.schulnummer}/mobil/mobdaten/PlanKl{date}.xml"

        driver.get(link)
        time.sleep(1)
        data = str((driver.find_element(selenium.webdriver.common.by.By.CLASS_NAME, "pretty-print").text).encode("ascii", "ignore"))

        driver.quit()

        print(data) #Debug