from selenium.webdriver.chrome.options import Options
import requests
import os
import pandas as pd
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import geopy.distance

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")

# URL and starting point
start_point = "서울기술교육센터"
url = f"https://m.map.naver.com/search2/search.naver?query=%EC%84%9C%EC%9A%B8%EA%B8%B0%EC%88%A0%EA%B5%90%EC%9C%A1%EC%84%BC%ED%84%B0&sm=hty&style=v5"

# Initialize WebDriver
driver = wb.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get(url)

# Wait for the page to load
time.sleep(10)

# Initialize lists to store data
shop_name = []
stars = []
addresses = []
categories = []
src = []

# Scroll and collect data
try:
    while True:
        last_height = driver.execute_script("return arguments[0].scrollHeight", body)
        driver.execute_script("arguments[0].scrollTop += 1200;", body)
        time.sleep(1)
        new_height = driver.execute_script("return arguments[0].scrollHeight", body)
        if new_height == last_height:
            break
        last_height = new_height

    data = driver.find_elements(By.CLASS_NAME, "TYaxT")
   #button = driver.find_element(By.XPATH, '//*[@id="app-layout"]/div[1]/div/div[2]/ul/li[1]/button/img')
    for i in range(len(data)):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame("searchIframe")
            data = driver.find_elements(By.CLASS_NAME, "TYaxT")
            if i >= len(data):
                break
            shop_name.append(data[i].text)
            data[i].click()
            time.sleep(2)
            driver.switch_to.default_content()
            driver.switch_to.frame("entryIframe")
            address = driver.find_element(By.CLASS_NAME, "LDgIH")
            addresses.append(address.text)
            category = driver.find_element(By.CLASS_NAME, "lnJFt")
            categories.append(category.text.split(','))
            try:
                src.append(driver.find_element(By.XPATH, '//*[@id="ibu_1"]').get_attribute("src"))
            except:
                src.append('')
            try:
                stars.append(driver.find_elements(By.CSS_SELECTOR, ".LXIwF")[0].text.split("\n")[1])
            except:
                stars.append('0')
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
            print(f"An error occurred: {e}")
            continue
except Exception as e:
    print(f"An error occurred during data collection: {e}")
finally:
    driver.quit()


# if button.get_attribute("aria-disabled") == "false":
   #     driver.switch_to.default_content()
   #     driver.switch_to.frame("searchIframe")
   #     button.click()
   #     time.sleep(3)
   # else:
   #     break


# Save data to CSV
with open("shop.csv", "w", newline="", encoding="CP949") as file:
    writer = csv.writer(file)
    header = ["상호명", "별점", "주소", "카테고리", "이미지"]
    writer.writerow(header)
    for i in range(len(shop_name)):
        writer.writerow([shop_name[i], stars[i], addresses[i], categories[i], src[i]])

# Read CSV and modify addresses
df = pd.read_csv("shop.csv", encoding="CP949")
for i in range(len(df)):
    if df["주소"][i] == "서울 강서구 내발산동 강서로 289":
        df["주소"][i] = "내발산동 701-9"

# Calculate distances
distance = []
for i in range(len(df)):
    address = df["주소"][i]
    url = f'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}'
    headers = {
        "X-NCP-APIGW-API-KEY-ID": os.getenv("NAVERMAP_API_KEY_ID"),
        "X-NCP-APIGW-API-KEY": os.getenv("NAVERMAP_API_KEY")
    }
    try:
        data = requests.get(url, headers=headers).json()
        x = data["addresses"][0]['x']
        y = data["addresses"][0]['y']
        dis = geopy.distance.distance((37.5423051, 126.8412894), (y, x)).km
        dis = round(dis * 1000, 0)
        distance.append(int(dis))
    except Exception as e:
        print(f"An error occurred while calculating distance for address {address}: {e}")
        distance.append(None)

df["거리"] = distance
df.to_csv("shop_distance.csv", encoding="CP949")
