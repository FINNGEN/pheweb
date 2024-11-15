import pytest
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from testcontainers.compose import DockerCompose
import os
import sys
import tempfile

this = sys.modules[__name__]
this.ENDPOINT : str ="http://pheweb:8080"
this.DELAY : int = 5

@pytest.fixture(scope="package")
def selinum_driver():
    # development mode
    development_host=os.getenv('DEVELOPMENT_HOST', default = None)
    development_image=os.getenv('DEVELOPMENT_IMAGE', default = None)

    if development_host is not None:
        this.ENDPOINT=development_host
        yield webdriver.Chrome()
    # handle being passed an image
    # otherwise build image
    else:
        if development_image is not None:
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
                temp_file.write(f"PHEWEB_IMAGE={development_image}")
                env_file = temp_file.name
            compose = DockerCompose("tests/integration/data/empty",
                                    compose_file_name="image-docker-compose.yaml",
                                    env_file=env_file)
        else:
            compose = DockerCompose("tests/integration/data/empty",
                                    compose_file_name="build-docker-compose.yaml")
        with compose:
            time.sleep(this.DELAY)
            options = webdriver.ChromeOptions()
            driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub',
                                      options=options)
            with driver as driver:
                yield driver

@pytest.mark.integration                
def test_about_click(selinum_driver):
    selinum_driver.maximize_window()
    selinum_driver.get(this.ENDPOINT)
    link=selinum_driver.find_element(By.PARTIAL_LINK_TEXT, "About")
    link.click()
    time.sleep(this.DELAY)
    selinum_driver.find_element(By.ID, "656245e9-53ba-4cb6-ac83-878a90ac4be5")

@pytest.mark.integration
def test_main_search(selinum_driver):
    selinum_driver.get(this.ENDPOINT)
    search=selinum_driver.find_element(By.ID, "react-select-2-input")
    search.send_keys("APOE")
    time.sleep(this.DELAY)
    search.send_keys(Keys.RETURN)
    #time.sleep(this.DELAY)
    #selinum_driver.find_element(By.ID, "gene-description")
