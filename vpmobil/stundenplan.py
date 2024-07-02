import selenium
import selenium.webdriver
import selenium.webdriver.common.by
import chromedriver_autoinstaller
import time

class Stundenplan():
    def __init__(self, schulnummer, benutzername, passwort):
        self.schulnummer = schulnummer
        self.benutzername = benutzername
        self.passwort = passwort
        #self.visiblewindow = False # TODO

    def fetch(self, date):
        chromedriver_autoinstaller.install()

        driver = selenium.webdriver.Chrome()

        link = "http://" + self.benutzername + ":" + self.passwort + "@stundenplan24.de/" + self.schulnummer + "/mobil/mobdaten/PlanKl" + "date" + ".xml"

        driver.get(link)

        time.sleep(1)

        data = str((driver.find_element(selenium.webdriver.common.by.By.CLASS_NAME, "pretty-print").text).encode("ascii", "ignore"))

        driver.quit()

        print(data) #Debug