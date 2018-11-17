import sys
sys.path.append("./lib")
sys.path.append(".")
from bs4 import BeautifulSoup
import requests 
from stock_db import StockDb
from pandas import DataFrame
import sqlite3
import time

db = StockDb()

def add_candidate_pool():
    sql_cmd = "select date,stock_id from (select * from tb_daily_info where pchg!='' and pchg>9 group by stock_id)"
    ret = db.query_db(sql_cmd)
    df = DataFrame(ret)
    df.columns = ['a','b']
    print(df)

if __name__ == '__main__': 
    add_candidate_pool()
    
