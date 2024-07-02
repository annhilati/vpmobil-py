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

    def fetch(self, date: int, browser: str = "Chrome"):
        """
        Creates a vpDay object containing all information about a specific day

        - date: Specific day in yyyymmdd format
        - browser: "Chrome", "Edge", "Firefox" or "Safari"
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

        data = driver.find_element(selenium.webdriver.common.by.By.CLASS_NAME, "pretty-print").text
        data = data.strip()

        driver.quit()

        return vpDay(xml=data) 
            
class vpDay():
    def __init__(self, xml: str):
        self.xml = xml

    def out(self, returnformat: str = "str"):
        """
        Returns all the information of the day in a certain format

        - returnformat: "str" or "ElementTree"
        """
        match returnformat:
            case "str":
                return ET.tostring(ET.ElementTree(ET.fromstring(self.xml)).getroot(), encoding="utf-8", method="xml")
            case "ElementTree":
                return ET.ElementTree(ET.fromstring(self.xml))
            case _:
                raise ValueError(f"Unsupported type: {returnformat}")