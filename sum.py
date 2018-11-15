import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil
import time
import datetime
from stock_mailer import StockMailer
from stock_db import StockDb
import pandas as pd

def test():
    data = [['Alex',10],['Bob',12],['Clarke',13]]
    df = pd.DataFrame(data,columns=['Name','Age'])
    h = df.to_html()
    print(h)

def summarize():
    yesterday = get_yesterday()
    file_name = "output/fp_%s.csv"%(yesterday)
    today = get_today()
    output_file_name = "output/summary_%s.csv"%(today)
    t = StockUtil()
    s_list = t.get_stock_list_from_file(file_name)
    f = open(output_file_name,'w')
    f.write("股票名称（股票ID）| 开盘涨幅 | 当前涨幅 | 当前价格 | 成交量（万手）| 成交金额（亿）\n")
    for s in s_list:
        info = t.get_live_mon_items(s)
        f.write(info)
        f.write('\n')
    f.close()

def sum():
    db = StockDb()
    stock_list = db.get_trading_stock_list()
    count = 0
    print("StockID | 3日涨幅 | 5日涨幅 | 7日涨幅 | 3日换手 | 5日换手 | 7日换手")  
    for s in stock_list:
        count = count+1
        if count==100:
            break              
        pchg_3 = round(db.get_sum_n_pchg(s,3),2)
        pchg_5 = round(db.get_sum_n_pchg(s,5),2)
        pchg_7 = round(db.get_sum_n_pchg(s,7),2)
        to_3 = round(db.get_sum_n_turnover(s,3),2)
        to_5 = round(db.get_sum_n_turnover(s,5),2)
        to_7 = round(db.get_sum_n_turnover(s,7),2)
        print("%s | %s | %s | %s | %s | %s | %s"%(s,pchg_3,pchg_5,pchg_7,to_3,to_5,to_7))


if __name__ == '__main__':       
    #monitor(file_name,60)
    #monitor_after_bid(file_name,60)
    sum()
    #send_sum_mail()