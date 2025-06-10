import requests
import time
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime
import os
from sqlalchemy import create_engine, text #engine을 통해 db접속
import pymysql
pymysql.install_as_MySQLdb()

company_infos=[]
page=1
while True:
    url="https://kind.krx.co.kr/corpgeneral/corpList.do"
    payload=dict(method='searchCorpList', pageIndex=page, currentPageSize=100, orderMode=3, orderStat='D', searchType=13, fiscalYearEnd='all', location='all')
    r=requests.post(url, data=payload)
    print(r.status_code)
    soup=bs(r.content, 'lxml')
    time.sleep(5)
    total_page=int(soup.select_one('.info.type-00 em').text.replace(",","")) // 100 + 1
    for idx, tr in enumerate(soup.select('tbody > tr')):
        print(f"{page}/{total_page}", end='\r')
        print(f'{idx+1}/{len(soup.select("tbody > tr"))} 작업중', end='\r')
        # 주식종목
        stock_type=tr.select_one('td:nth-child(1) img')['alt']
        #회사명
        company_name=tr.select_one('td:nth-child(1) > a')['title']
        # 종목코드
        stock_code=tr.select_one('td:nth-child(1) > a')['onclick'].split("'")[1]
        # 업종
        business_type=tr.select_one('td:nth-child(2)').text
        # 주요제품
        product=tr.select_one('td:nth-child(3)').text
        # 상장일
        resi_date=tr.select_one('td:nth-child(4)').text
        # 결산월
        settlement=tr.select_one('td:nth-child(5)').text
        # 대표자명
        ceo=tr.select_one('td:nth-child(6)')['title']
        # 홈페이지
        homepage=tr.select_one('td:nth-child(7) > a')['href'] if tr.select_one('td:nth-child(7) > a')!=None else ""
        # 지역
        region=tr.select_one('td:nth-child(8)').text
        company_infos.append((stock_type, company_name, stock_code, business_type, product,
                            resi_date, settlement, ceo, homepage, region))

    if page < total_page:
        page+=1
    else:
        break
# 컬럼명
columns=soup.select_one(".list.type-00.tmt30")['summary'].split(", ")
columns.insert(0, '주식종목')
columns.insert(2, '종목코드')
print(columns)
df=pd.DataFrame(company_infos, columns=columns)


today=datetime.now()
date=(f"{today.year}.{today.month:02d}.{today.day:02d}")

# 폴더 자동생성
if not os.path.exists("./scraping_results"):
    os.mkdir("./scraping_results")

df.to_csv(f"./scraping_results/상장기업정보_{date}기준.csv", encoding='utf-8', index=False)
print("./scraping_results/상장기업정보_{today}기준.csv 저장완료")
engine=create_engine("mysql+pymysql://root:1234@localhost:3306/stock_info")
# create_engine에 있는 정보로 db 접속
conn=engine.connect()
df.to_sql(f"stock_company_info_{today}", con=conn, if_exists='replace', index=False)
print(f"stock_company_info_{today} 데이터베이스 저장완료!")
conn.close()