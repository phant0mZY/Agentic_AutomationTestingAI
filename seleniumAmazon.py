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
wait=WebDriverWait(driver,20)
search=wait.until(EC.presence_of_element_located((By.ID,"twotabsearchtextbox")))

search.send_keys("laptop")
search.send_keys(Keys.RETURN)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.s-main-slot")))

firstproduct=driver.find_element(By.CSS_SELECTOR,"div.s-main-slot div[data-component-type='s-search-result']")
firstproduct.find_element(By.TAG_NAME,"h2").click()
time.sleep(3)

driver.switch_to.window(driver.window_handles[1])
try:
    addcart=wait.until(EC.element_to_be_clickable((By.ID,"add-to-cart-button")))
    addcart.click()
    print("Product added to cart successfully.")

except:
    print("failed")

time.sleep(5)
driver.quit()