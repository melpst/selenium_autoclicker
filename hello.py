from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from dotenv import load_dotenv

import os
import time
import re

def main():
    print('Start scraping')
    
    """
        1. open web
        2. login
        3. go to recently watch
        4. click the first one
        5. click bottom img
        6. click latest watched+1 episode

        loop from here
        7. full screen
        8. sleep until end
        9. quit full screen
        10. next episode

        end loop if no more episode
        quit
    """

    load_dotenv()
    url = os.getenv('URL')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)

    driver.get(url)
    login(driver, username, password)
    goto(driver, By.CLASS_NAME, 'recent-carousel')
    goto(driver, By.CLASS_NAME, 'season')
    time.sleep(10)

    driver.quit()

    print('Quit successfully')

def login(driver: WebDriver, username: str, password: str):
    driver.find_element(by=By.ID, value="solo_login_email").send_keys(username)
    driver.find_element(by=By.ID, value="solo_login_password").send_keys(password)
    driver.find_element(by=By.CLASS_NAME, value="btn-login").click()
    time.sleep(1)

def goto(driver: WebDriver, find_by: str, value: str):
    print('goto', value)
    element = driver.find_element(by=find_by, value=value)
    element.find_element(by=By.CSS_SELECTOR, value="a").click()
    time.sleep(1)
main()