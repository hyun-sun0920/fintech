from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()
import pandas as pd

def dbconnect():
    engine=create_engine("mysql+pymysql://root:1234@localhost:3306/stock_info")
    conn=engine.connect()
    return conn

def get_today_yyyymm():
    today = datetime.today()
    return f"{today.year}{today.month:02d}"


def stock_codes():
    conn= dbconnect()
    data =pd.read_sql('stock_company_info_{today}', con=conn)
    conn.close()
    stock_code=data['종목코드'].apply(lambda x: x+"0")
    return stock_code

def to_stock_db(idx, stock_code, stock_name, df):
    #오늘기준 연도, 달 출력
    year, month = year_month()
    # Database 쿼리창 오픈
    conn= dbconnect()
    df.to_sql(f'stock_price'_{year}_{month:02d}', con=conn, if exists="append", index=False)
    conn.close()
    print(f"{idx+1}/{len(stock_code)}{stock_name}DB 저장 완료", end="\r")
    return