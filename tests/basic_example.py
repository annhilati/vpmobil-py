# This is a basic example of a script that connects to VP Mobil and prints a plan
# Requirements: chromedriver_autoinstaller, selenium

import selenium
import selenium.webdriver
import selenium.webdriver.common.by
import chromedriver_autoinstaller
import time


chromedriver_autoinstaller.install() # Checks if chromedriver is downloaded and installs it when not

driver = selenium.webdriver.Edge() # You can change this to Firefox, IE, Safari or Edge | Browser has to be installed on your system

link = "http://schueler:s361o97@stundenplan24.de/10126582/mobil/mobdaten/PlanKl" + "20240619" + ".xml" # Formlua to access plan for any date | Date Format: yyyymmdd

driver.get(link) # Open the link in the browser

time.sleep(1) # wait to make sure the page is fully loaded

data = str((driver.find_element(selenium.webdriver.common.by.By.CLASS_NAME, "pretty-print").text).encode("ascii", "ignore"))
# Get the element by class name 'pretty-print', grap the text inside it and encode it in ascii

driver.quit() # Close the window and kill the driver

print(data) # Print the data