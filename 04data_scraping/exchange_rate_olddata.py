def new_col(df):
    new_cols = []
    for col in df.columns:
        if col[0] == col[1] == col[2]:
            new_cols.append(col[0].replace(" ", "_"))
        else:
            new_cols.append(" ".join(col).strip().replace(" ", "_"))
    return new_cols

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import datetime
from io import StringIO
import time
from ex_dbio import to_ex_db   

options = Options()
options.add_experimental_option("detach", True)
options.add_argument("start-maximized")
options.add_argument("Chrome/135.0.0.0")
options.add_argument("lang=ko_KR")
#웹 브라우저가 백그라운드에서 작동하도록 설정
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
    )

url = "https://www.kebhana.com/cms/rate/index.do?contentUrl=/cms/rate/wpfxd651_01i.do"
driver.get(url)
time.sleep(5)
wait = WebDriverWait(driver, 60)


# 시작일과 끝일 입력해서 날짜 리스트 생성
start_date = datetime.date(1995, 1, 3)
end_date = datetime.date(2025, 4, 10)

date_list = []
while start_date <= end_date:
    # 평일인지 필터링
    if start_date.weekday() < 5:
        date_list.append(start_date)
    start_date += datetime.timedelta(days = 1)

for date in date_list:
    try: 
    # 날짜 입력
    
        date_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tmpInqStrDt")))
        date_input.clear()
        date_input.send_keys(str(date).replace("-", ""))
        date_input.send_keys(Keys.ENTER)

        # 조회버튼 클릭
        search_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#HANA_CONTENTS_DIV > div.btnBoxCenter > a")))
        search_button.click()
    except Exception:
        print(f"{date}데이터 수집 오류")
        with open("exchange_rate_error_logs.txt", "a") as f:
            f.write(f"{date}데이터 수집 오류\n")
        
    
    
    # 수집한 데이터를 바탕으로 데이터프레임 만듬.
    df = pd.read_html(StringIO(driver.find_element(By.CSS_SELECTOR, ".tblBasic.leftNone").get_attribute('outerHTML')))[0]
    df['date'] = date
    new_columns = new_col(df)
    df.columns = new_columns
    df = df[['date', '통화', '현찰_사실_때_환율', '현찰_사실_때_Spread', '현찰_파실_때_환율', '현찰_파실_때_Spread',
       '송금_보낼_때_보낼_때', '송금_받을_때_받을_때', '외화_수표_파실때', '매매_기준율', '환가_료율',
       '미화_환산율']]
    to_ex_db(df)
    print(f"{date} 환율정보 DB 저장 완료", end="\r")