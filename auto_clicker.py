from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from typing import List, Dict
import os
import time
import re

load_dotenv(override=True)

TIMEOUT = 30
DELAY = 1
INTRO = 100
OUTRO = 150

SKIP_TO_EPISODE = None
EPISODE_TO_WATCH = None

def create_driver() -> WebDriver:
    driver: WebDriver = webdriver.Chrome(
        options = Options().add_argument('user-data-dir=selenium')
    )

    driver.implicitly_wait(TIMEOUT)
    driver.set_page_load_timeout(TIMEOUT)

    return driver

def add_cookies(driver: WebDriver) -> WebDriver:
    base_cookie: Dict[str, str] = {
        'domain': os.getenv('DOMAIN'),
        'path': '/'
    }

    # enable network to edit cookie
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setCookie', 
                            {
                                'name': 'lem',
                                'value': os.getenv('lem'),
                                **base_cookie
                            })
    driver.execute_cdp_cmd('Network.setCookie', 
                            {
                                'name': 'user_loggedsession',
                                'value': os.getenv('session'),
                                **base_cookie
                            })
    driver.execute_cdp_cmd('Network.disable', {})

    return driver

def main():
    print('Start scraping')
    
    driver: WebDriver = add_cookies(create_driver())
    driver.get(os.getenv('URL'))

    goto(driver, By.CLASS_NAME, 'recent-carousel')
    goto(driver, By.CLASS_NAME, 'season')

    (current, left) = search_for_unwatched_episode(driver)
    loop(driver, current, left)
    
    time.sleep(DELAY)
    driver.quit()
    print('Quit successfully')

def goto(driver: WebDriver, find_by: str, value: str) -> None:
    print('goto', value)
    element: WebElement = driver.find_element(by=find_by, value=value)
    element.find_element(by=By.CSS_SELECTOR, value='a').click()
    time.sleep(DELAY)

def search_for_unwatched_episode(driver: WebDriver) -> List[int]:
    elements: List[WebElement] = driver.find_elements(by=By.CLASS_NAME,value='progress-bar-danger')
    not_played: List[WebElement] = list(filter(
            lambda x: int(re.findall(r'\d+', x.get_attribute('style'))[0]) < 90, elements
        ))
    
    not_played[0].find_element(by=By.XPATH, value='..').click()
    time.sleep(DELAY)
    
    return [len(elements)-len(not_played)+1,len(not_played)]
    
def toggle_full_screen(driver: WebDriver) -> None:
    time.sleep(3)
    control_panel: WebElement = driver.find_element(by=By.CLASS_NAME, value='media-control')
    driver.execute_script("arguments[0].setAttribute('class', 'media-control')", control_panel)
    time.sleep(DELAY)
    
    elements: List[WebElement] = driver.find_elements(by=By.CLASS_NAME, value='media-control-button')
    list(filter(lambda x: x.accessible_name == 'fullscreen', elements))[0].click()
    time.sleep(DELAY)

def get_duration(driver: WebDriver) -> int:
    video: WebElement = driver.find_element(by=By.CSS_SELECTOR, value='video')
    current_time: int = int(video.get_property('currentTime'))
    duration: int = int(video.get_property('duration'))

    return duration-current_time-OUTRO

def skip_to_episode(driver: WebDriver, episode: int) -> List[int]:
    episodes: List[WebElement] = driver.find_elements(by=By.CLASS_NAME, value='carousel-cell-left_subtitle')
    
    if len(episodes)<episode:
        return [-1, -1]
    
    print(f'skip to episode {episode}')
    episodes[episode-1].click()
    time.sleep(DELAY)
    
    return [episode, len(episodes)-episode]

def loop(driver: WebDriver, current: int, left: int) -> None:
    for i in range(0, left):
        print(f'currently playing episode {current+i}')
        time.sleep(5)
        toggle_full_screen(driver)
        
        interval: int = get_duration(driver)
        print(interval)
        time.sleep(interval)
        toggle_full_screen(driver)
        
        next_button: WebElement = driver.find_element(By.ID, 'solo-serieplay-ep-next')
        if next_button is not None:
            next_button.click()
        else:
            print('where is next button?')
            break

    print('watched all~~~')
    
main()