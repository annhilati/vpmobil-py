import selenium
import selenium.webdriver
import selenium.webdriver.common.by
import chromedriver_autoinstaller
import time
import xml.etree.ElementTree as ET

class Stundenplan():
    """
    Refers to a specific account on a specific VpMobil-Stundenplan
    """
    def __init__(self, schulnummer: int, benutzername: str, passwort: str):
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort

    def fetch(self, date: int, browser: str = "Chrome", returntype: str = "str") -> ET.Element:
        """
        Prints all the information of a specific day as XML

        - date: Specific day in yyyymmdd format
        - browser: "Chrome", "Edge", "Firefox" or "Safari"
        - returntype: "str" or "XML"
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
            case _:
                raise ValueError(f"Unsupported browser: {browser}")
            

        uri = f"http://{self.benutzername}:{self.passwort}@stundenplan24.de/{self.schulnummer}/mobil/mobdaten/PlanKl{date}.xml"

        driver.get(uri)
        time.sleep(1)
        data = str((driver.find_element(selenium.webdriver.common.by.By.CLASS_NAME, "pretty-print").text).encode("ascii", "ignore"))

        driver.quit()

        match returntype:
            case "str":
                return data
            case "XML":
                return ET.fromstring(data)
            case _:
                raise ValueError(f"Unsupported type: {returntype}")