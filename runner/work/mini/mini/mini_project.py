# 라이브러리 모음
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
# 이미지 저장하기 위해 요청 라이브러리 필요
import requests
import os # 폴더 생성
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")  # 포트 지정
start_point = "서울기술교육센터"
url = f"https://map.naver.com/p/search/%EC%84%9C%EC%9A%B8%EA%B8%B0%EC%88%A0%EA%B5%90%EC%9C%A1%EC%84%BC%ED%84%B0?c=15.00,0,0,0,dh"
driver = wb.Chrome(options=chrome_options)
driver.get(url)
time.sleep(1)
driver.switch_to.default_content()
driver.switch_to.frame("searchIframe")
Advertisement = driver.find_elements(By.CLASS_NAME, "dPXjn")
data = driver.find_elements(By.CLASS_NAME, "YwYLL")
start_point_name = data[len(Advertisement)]
time.sleep(0.5)
start_point_name.click()
time.sleep(0.5)
driver.back()
shop = driver.find_element(By.CLASS_NAME, "bubble_keyword_text")
shop.click()
time.sleep(2)
driver.switch_to.default_content()
driver.switch_to.frame("searchIframe")  # 프레임 전환(가게 목록)
body = driver.find_element(By.CLASS_NAME, "Ryr1F")
shop_name = []
stars = []
addresses = []
categories = []
src = []
while True:
        last_height = driver.execute_script("return arguments[0].scrollHeight", body)
        # 요소 내에서 아래로 600px 스크롤
        driver.execute_script("arguments[0].scrollTop += 1200;", body)
        # 페이지 로드를 기다림
        time.sleep(1)  # 동적 콘텐츠 로드 시간에 따라 조절
        # 새 높이 계산
        new_height = driver.execute_script("return arguments[0].scrollHeight", body)
        # 스크롤이 더 이상 늘어나지 않으면 루프 종료
        if new_height == last_height:
            break
        last_height = new_height
data = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]/ul/li/div[1]/a[1]/div/div/span[1]') # 음식점 상호명(개수 세기 위해)
button =  driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div[2]/div[2]/a[7]') # 페이지 넘기는 버튼 (>)
while True:
    i = 0
    while True:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame("searchIframe")
            data = driver.find_elements(By.CLASS_NAME, "TYaxT") # 음식점 상호명
            shop_name.append(data[i].text)
            data[i].click()
            time.sleep(2)
            driver.switch_to.default_content()
            driver.switch_to.frame("entryIframe") # 프레임 전환(가게 상세 페이지)
            address = driver.find_element(By.CLASS_NAME, "LDgIH")
            addresses.append(address.text) # 가게 주소
            category = driver.find_element(By.CLASS_NAME, "lnJFt")
            categories.append(category.text.split(',')) # 가게 카테고리
            try:
                src.append(driver.find_element(By.XPATH, '//*[@id="ibu_1"]').get_attribute("src"))
            except:
                src.append('')
            try:
                stars.append(driver.find_elements(By.CSS_SELECTOR, ".LXIwF")[0].text.split("\n")[1]) # 별점
            except:
                stars.append('0')
            i += 1
        except:
            break
    if button.get_attribute("aria-disabled") == "false":
        driver.switch_to.default_content()
        driver.switch_to.frame("searchIframe") # 프레임 전환(가게 목록)
        button.click() # 페이지 넘기는 버튼 클릭
        time.sleep(3)
    else:
        break
import csv
with open("shop.csv", "w", newline="", encoding="CP949") as file:
    writer = csv.writer(file)
    header = ["상호명", "별점", "주소", "카테고리", "이미지"]
    writer.writerow(header)
    for i in range(len(shop_name)):
        writer.writerow([shop_name[i], stars[i], addresses[i], categories[i], src[i]])
import pandas as pd
df = pd.read_csv("shop.csv", encoding="CP949")
for i in range(len(df)):
    if df["주소"][i] == "서울 강서구 내발산동 강서로 289":
        df["주소"][i] = "내발산동 701-9"
import geopy.distance # 거리계산 라이브러리
distance = []
for i in range(len(df)):
    address = df["주소"][i]
    url = f'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}' #주소입력
    headers = {
        "X-NCP-APIGW-API-KEY-ID": os.getenv("NAVERMAP_API_KEY_ID"),
        "X-NCP-APIGW-API-KEY": os.getenv("NAVERMAP_API_KEY")
    } # header에 api-key
    data = requests.get(url,headers=headers).json()
    x =data["addresses"][0]['x']
    y =data["addresses"][0]['y']
    dis = geopy.distance.distance((37.5423051, 126.8412894), (y,x)).km
    dis = round(dis * 1000, 0)
    distance.append(int(dis)) #(37.5423051, 126.8412894) =>대한상공회의소 좌표
df["거리"] = distance
df.to_csv("shop_distance.csv", encoding="CP949")
