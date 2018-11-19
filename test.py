import sys
sys.path.append("./lib")
sys.path.append(".")
from bs4 import BeautifulSoup
import requests 
from stock_db import StockDb
from pandas import DataFrame
import sqlite3
import time
from pandas.io import sql

db = StockDb()

def add_candidate_pool():
    sql_cmd = "select date,stock_id from (select * from tb_daily_info where pchg!='' and pchg>9 group by stock_id)"
    ret = db.query_db(sql_cmd)
    df = DataFrame(ret)
    df.columns = ['add_date','stock_id']
    conn = sqlite3.connect(db.db_name)
    print(df)
    df.to_sql(name='tb_candidate_pool',con=conn,if_exists='replace',index=False)

def get_low_score():
    sql_cmd = "select date,stock_id,score from (select date,stock_id,turnover,pchg,t1,t2,t3,pchg+t1+t2+t3 as score \
        from (select *,(close-high)*100/close as t1,(close-open)*100/open as t2, (close-low)*100/low as t3, \
        (high-low)*100/low as t4 from tb_daily_info)) where score<-10"
    ret = db.query_db(sql_cmd)
    df = DataFrame(ret)
    print(df)
    df.to_csv('test.csv')

def get_sum_score():
    sql_cmd = "select date,stock_id,sum(score) from (select date,stock_id,turnover,pchg,t1,t2,t3,pchg+t1+t2+t3 as score \
        from (select *,(close-high)*100/close as t1,(close-open)*100/open as t2, (close-low)*100/low as t3, \
        (high-low)*100/low as t4 from tb_daily_info) group by stock_id)"
    ret = db.query_db(sql_cmd)
    df = DataFrame(ret)
    print(df)

def get_stock_score_list(stock_id,date):
    sql_cmd = "select date,stock_id, score from (select date,stock_id,turnover,pchg,t1,t2,t3,pchg*3+t1+t2+t3 as score from \
    (select *,(close-high)*100/close as t1,(close-open)*100/open as t2, (close-low)*100/low as t3, (high-low)*100/low as t4 \
    from tb_daily_info where date>'%s' and stock_id='%s') order by date desc)"%(date,stock_id)
    ret = db.query_db(sql_cmd)
    try:
        df = DataFrame(ret)
        ret = df[2].values.tolist()
    except:
        print("exception on stock %s"%(stock_id))
    #print(df)
    return ret

def get_weighted_score(stock_id,date='2018-11-01'):
    score_list = get_stock_score_list(stock_id,date)
    ret = 0
    count = 1
    for score in score_list:
        ret = ret+score*count
        count = count/2
    return ret

def get_stock_list_from_pool(date):
    sql_cmd = "select stock_id from tb_candidate_pool where add_date>'%s'"%(date)
    ret = db.query_db(sql_cmd)
    df = DataFrame(ret)
    return df[0].values.tolist()

if __name__ == '__main__': 
    #add_candidate_pool()
    #get_low_score()
    #get_sum_score()
    #score_list = get_stock_score_list('2018-11-01','sh600604')
    #print(get_weighted_score('sz000622'))
    #print(get_stock_list_from_pool())
    date = '2018-11-01'
    s_list = get_stock_list_from_pool(date)
    for s in s_list:
        score = get_weighted_score(s,date)
        if score<0:
            print("Stock:%s,score:%s"%(s,score))
    
