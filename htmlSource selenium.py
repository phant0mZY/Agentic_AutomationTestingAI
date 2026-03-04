from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options=webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver=webdriver.Chrome(options=options)

driver.get("https://www.amazon.in")
time.sleep(3)

source=driver.page_source
wait=WebDriverWait(driver,20)

with open("source.txt","w",encoding="utf-8") as f:
    f.write(source)