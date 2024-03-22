#!/bin/env python3
from selenium import webdriver
import time
from selenium.webdriver.common.by import By

print("Test Execution Started")
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Remote(
command_executor='http://localhost:4444/wd/hub',
options=options
)
with driver as driver:
    #maximize the window size
    driver.maximize_window()
    time.sleep(10)
    #navigate to browserstack.com
    driver.get("https://www.browserstack.com/")
    time.sleep(10)
    #click on the Get started for free button
    driver.find_element(By.PARTIAL_LINK_TEXT, "About")
    time.sleep(10)
    #close the browser
    driver.close()

print("Test Execution Successfully Completed!")
