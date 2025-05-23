from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def kor2eng(keyword):


    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("start-maximized")
    options.add_argument("Chrome/135.0.0.0")
    options.add_argument("lang=ko_KR")
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
        )


    url = "https://translate.google.co.kr/?sl=ko&tl=en&op=translate"
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    search_text_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div > textarea")))
    search_text_box.send_keys(keyword)
    search_text_box.send_keys(Keys.ENTER)
    
    wait = WebDriverWait(driver, 10)
    kor_text_box=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div>textarea")))
    kor_text_box.send_keys(keyword)
    kor_text_box.send_keys(Keys.ENTER)
    
    translated_box= wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.IRu31 span. ryNqvb")))
    return translated_box.text