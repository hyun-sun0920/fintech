import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

print("프로그램이 시작되었습니다.")

try:
    url = "https://kind.krx.co.kr/corpgeneral/corpList.do"
    payload = dict(method="searchCorpList", pageIndex=1, currentPageSize=100, orderMode=3, orderStat="D", searchType=13, fiscalYearEnd="all", location="all")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.post(url, data=payload, headers=headers)
    print("요청 상태코드:", r.status_code)

    soup = bs(r.content, 'lxml')
    company_infos = []

    rows = soup.select("tbody > tr")
    print(f"총 {len(rows)}개의 행을 찾음")

    for idx, tr in enumerate(rows):
        print(f'{idx+1}/{len(rows)} 작업중')
        stock_type = tr.select_one("td:nth-child(1) > img")['alt']
        company_name = tr.select_one("td:nth-child(1) > a")["title"]
        stock_code = tr.select_one("td:nth-child(1) > a")["onclick"].split("'")[1]
        business_type = tr.select_one("td:nth-child(2)").text
        product = tr.select_one("td:nth-child(3)").text
        resi_date = tr.select_one("td:nth-child(4)").text
        settlement = tr.select_one("td:nth-child(5)").text
        ceo = tr.select_one("td:nth-child(6)").text
        hompage = tr.select_one("td:nth-child(7) > a")["href"] if tr.select_one("td:nth-child(7) > a") else ""
        region = tr.select_one("td:nth-child(8)").text

        company_infos.append((stock_type, company_name, stock_code, business_type,
                              product, resi_date, settlement, ceo, hompage, region))
    
    print("스크래핑 완료. 총 수집된 회사 수:", len(company_infos))

except Exception as e:
    print("에러 발생:", e)

input("엔터를 누르면 종료됩니다.")