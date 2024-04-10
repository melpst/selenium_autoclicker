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
OUTRO = 140

SKIP_TO_EPISODE = -1
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
        7. skip to episode -> exact match at class carousel-cell-left_title -> parent click
        8. login via api instead and get session -> skip login page
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
    
    (current_episode, left) = search_for_unwatched_episode(driver) if SKIP_TO_EPISODE < 1 else skip_to_episode(driver, SKIP_TO_EPISODE)
    print(current_episode, left)
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
        if next_button is not None:
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
    not_played = list(filter(lambda x: int(re.findall(r'\d+', x.get_attribute('style'))[0]) < 90, elements))
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
    current_time = int(video.get_property('currentTime'))
    duration = int(video.get_property('duration'))
    return duration-current_time-OUTRO

def skip_to_episode(driver: WebDriver, episode: int) -> List[int]:
    episodes = driver.find_elements(by=By.CLASS_NAME, value='carousel-cell-left_subtitle')
    wanted_episode = episodes[episode-1]
    left = len(episodes)-episode

    print(f'skip to episode {episode}')
    wanted_episode.click()
    time.sleep(DELAY)
    return [episode, left]
    
main()