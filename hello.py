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
    time.sleep(10)

    driver.quit()

    print('Quit successfully')

main()