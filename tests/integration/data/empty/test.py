
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

print(0)
with webdriver.Remote(command_executor='http://localhost:4444/wd/hub') as driver:
    print(1)
    driver.maximize_window()
    print(2)
    time.sleep(3)
    print(3)
    driver.get("http://pheweb:8080")
    print(4)
    time.sleep(3)
    print(5)
    link=driver.find_element(By.PARTIAL_LINK_TEXT, "About")
    print(6)
    link.click()
    print(7)
    time.sleep(3)
    print(8)
    driver.close()
print("Test Execution Successfully Completed!")
