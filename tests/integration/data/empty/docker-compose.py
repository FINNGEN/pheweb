#!/bin/env python3
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_for_logs

sentinel="Listening at:"

def main():
    compose = DockerCompose(".",
                            compose_file_name="docker-compose.yaml",
                            pull=True)
    with compose:
        time.sleep(20)
        print("Test Execution Started")
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub',
                                  options=options)
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

            driver.maximize_window()
            driver.get("http://pheweb:8080")
            link=driver.find_element(By.PARTIAL_LINK_TEXT, "About")
            link.click()


        stdout, stderr = compose.get_logs()


if __name__ == "__main__":
    main()
