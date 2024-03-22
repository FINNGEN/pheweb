#!/bin/env python3
from testcontainers.selenium import BrowserWebDriverContainer
from selenium.webdriver import DesiredCapabilities
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
import os
import time

sentinel="Listening at:"

#network_name = "my_custom_network"
#docker_client_kw = { "networks" : [ network_name ]}

def main():
    docker_container = DockerContainer("eu.gcr.io/phewas-development/pheweb:wip-509069f8c5d64d6096d2e97ff2b7c3b7e57e4d57")
    docker_container = docker_container.with_name("test_pheweb")
    docker_container = docker_container.with_volume_mapping(os.getcwd(), "/data/pheweb/test")
    docker_container = docker_container.with_env("PHEWEB_DIR", "/data/pheweb/test")
    docker_container = docker_container.with_exposed_ports(8080)
    print(dir(docker_container))
    with docker_container as pheweb:
        wait_for_logs(pheweb, lambda x : sentinel in x, timeout=120)
        with BrowserWebDriverContainer(DesiredCapabilities.CHROME) as chrome:
            with chrome.get_driver() as driver:
                driver.maximize_window()
                # print(dir(chrome))
                # print(chrome.connection_url())
                # print(chrome.get_container_host_ip())
                # print(chrome.get_docker_client())
                print("....................")
                print(dir(pheweb))
                print(pheweb.get_container_host_ip())
                print(pheweb.get_docker_client())
                url = f"http://192.168.8.172:8080"
                print(url)
                time.sleep(10)
                driver.get(url)
                about=driver.find_element(By.PARTIAL_LINK_TEXT, "About").click()

                # print(pheweb)
                # print(pheweb._name)
                # print(pheweb.get_container_host_ip())
                # print(pheweb.get_docker_client())
                # print(pheweb.get_wrapped_container())
                # print(dir(pheweb))
                # print(pheweb.get_logs())
if __name__ == "__main__":
    main()
