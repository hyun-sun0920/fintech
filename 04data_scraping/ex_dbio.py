
from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()
import pandas as pd
import time

def dbconnect():
    engine=create_engine("mysql+pymysql://root:1234@localhost:3306/exchange_rate")
    conn=engine.connect()
    return conn


def to_ex_db(df):
    conn = dbconnect()
    time.sleep(2)
    df.to_sql('exchange_rate', con=conn, if_exists="replace", index=False)
    conn.close()
