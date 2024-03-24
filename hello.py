from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def main():
    print("Start scraping")


    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    time.sleep(1)

    submit_button = driver.find_element(by = By.CSS_SELECTOR, value="button")
    submit_button.click()
    time.sleep(1)

    driver.quit()

    print("Quit successfully")

main()