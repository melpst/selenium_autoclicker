from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

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

load_dotenv(override=True)

def create_driver() -> WebDriver:
    browser_options = Options()
    browser_options.add_argument("user-data-dir=selenium")

    driver: WebDriver = webdriver.Chrome(options=browser_options)
    driver.implicitly_wait(TIMEOUT)
    driver.set_page_load_timeout(TIMEOUT)

    return driver

def add_cookies(driver: WebDriver) -> WebDriver:
    base_cookie: dict[str, str] = {
        'domain': os.getenv('DOMAIN'),
        'path': '/'
    }
    lem: dict[str, str] = {
        'name': 'lem',
        'value': os.getenv('lem')
    }
    session: dict[str, str] = {
        'name': 'user_loggedsession',
        'value': os.getenv('session')
    }
    
    lem.update(base_cookie)
    session.update(base_cookie)

    # enable network to edit cookie
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setCookie', lem)
    driver.execute_cdp_cmd('Network.setCookie', session)
    driver.execute_cdp_cmd('Network.disable', {})

    return driver

def main():
    print('Start scraping')
    
    """
        improvement
        1. skip intro
        2. write as OOP
        3. maybe also functional?
        4. add tests
        5. skip to episode
            - check if episode exist -> end program if not
            - if episode already played (>= duration-outro) -> play again since beginning
        6. login via api instead and get session -> can skip login page -> use serie url
    """

    driver: WebDriver = add_cookies(create_driver())
    driver.get(os.getenv('URL'))

    # login(driver, username, password)
    # goto(driver, By.CLASS_NAME, 'recent-carousel')
    # goto(driver, By.CLASS_NAME, 'season')
    
    # (current, left) = search_for_unwatched_episode(driver) if SKIP_TO_EPISODE < 1 else skip_to_episode(driver, SKIP_TO_EPISODE)
    # left = left if EPISODE_TO_WATCH<0 else EPISODE_TO_WATCH
    # loop(driver, current, left)
    
    time.sleep(DELAY)
    driver.quit()

    print('Quit successfully')

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
    
    if len(episodes)<episode:
        return [-1, -1]
    
    wanted_episode = episodes[episode-1]
    left = len(episodes)-episode

    print(f'skip to episode {episode}')
    wanted_episode.click()
    time.sleep(DELAY)
    return [episode, left]

def loop(driver: WebDriver, current: int, left: int) -> None:
    for i in range(0, left):
        print(f'currently playing episode {current+i}')
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
    
main()