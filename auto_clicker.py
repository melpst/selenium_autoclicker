from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from dotenv import load_dotenv

from typing import List
import os
import time
import re

TIMEOUT = 30
DELAY = 1
INTRO = 35
OUTRO = 10
EPISODE_TO_WATCH = -1

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

        improvement
        1. skip intro
        2. write as OOP
        3. maybe also functional?
        4. add tests
        5. store session
        6. skip login if session is valid
    """

    load_dotenv()
    url = os.getenv('URL')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    driver = webdriver.Chrome()
    driver.implicitly_wait(TIMEOUT)
    driver.set_page_load_timeout(TIMEOUT)

    driver.get(url)
    login(driver, username, password)
    goto(driver, By.CLASS_NAME, 'recent-carousel')
    goto(driver, By.CLASS_NAME, 'season')
    
    (current_episode, left) = search_for_unwatched_episode(driver)
    left = left if EPISODE_TO_WATCH<0 else EPISODE_TO_WATCH

    for i in range(0, left):
        print(f'currently playing episode {current_episode+i}')
        time.sleep(5)
        toggle_full_screen(driver)
        
        interval = get_duration(driver)
        print(interval)
        time.sleep(interval)
        toggle_full_screen(driver)
        
        next_button = driver.find_element(By.ID, 'solo-serieplay-ep-next')
        if next_button is not None and i<left-1:
            next_button.click()
        else:
            print('where is next button?')
            break

    print('watched all~~~')
    time.sleep(DELAY)
    driver.quit()

    print('Quit successfully')

def login(driver: WebDriver, username: str, password: str) -> None:
    driver.find_element(by=By.ID, value='solo_login_email').send_keys(username)
    driver.find_element(by=By.ID, value='solo_login_password').send_keys(password)
    driver.find_element(by=By.CLASS_NAME, value='btn-login').click()
    time.sleep(DELAY)

def goto(driver: WebDriver, find_by: str, value: str) -> None:
    print('goto', value)
    element = driver.find_element(by=find_by, value=value)
    element.find_element(by=By.CSS_SELECTOR, value='a').click()
    time.sleep(DELAY)

def search_for_unwatched_episode(driver: WebDriver) -> List[int]:
    elements = driver.find_elements(by=By.CLASS_NAME,value='progress-bar-danger')
    not_played = list(filter(lambda x: int(re.findall(r'\d+', x.get_attribute('style'))[0]) < 95, elements))
    not_played[0].find_element(by=By.XPATH, value='..').click()
    time.sleep(DELAY)
    return [len(elements)-len(not_played)+1,len(not_played)]
    
def toggle_full_screen(driver: WebDriver) -> None:
    control_panel = driver.find_element(by=By.CLASS_NAME, value='media-control')
    driver.execute_script("arguments[0].setAttribute('class', 'media-control')", control_panel)
    time.sleep(3)

    elements = driver.find_elements(by=By.CLASS_NAME, value='media-control-button')
    list(filter(lambda x: x.accessible_name == 'fullscreen', elements))[0].click()
    time.sleep(DELAY)

def get_duration(driver: WebDriver) -> int:
    video = driver.find_element(by=By.CSS_SELECTOR, value='video')
    duration = int(video.get_property('duration'))
    return duration-OUTRO

def skip_intro(driver):
    time.sleep(0.5)
    # video: WebElement = driver.find_element(by=By.CSS_SELECTOR, value='video')
    # video.click()
    # driver.execute_script(f"arguments[0].setAttribute('currentTime', {INTRO})", video)
    # video.click()

    control_panel = driver.find_element(by=By.CLASS_NAME, value='media-control')
    driver.execute_script("arguments[0].setAttribute('class', 'media-control')", control_panel)
    dot = driver.find_element(by=By.CLASS_NAME, value='bar-scrubber')
    driver.execute_script(f"arguments[0].setAttribute('style', 'left: 0.5%;')", dot)
    driver.find_element(by=By.CLASS_NAME, value='bar-scrubber')
    
main()