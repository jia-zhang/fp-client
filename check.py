import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil
import time
import datetime
from stock_mon import StockMon
from stock_db import StockDb
import pandas as pd

m = StockMon()
db = StockDb()
my_list = ['sz002567','sh603609']

def check():
    m = StockMon()    
    #Get top n and bottom n
    m.check_top_and_bottom(50)
    #Get zt and dt number
    print("zt number: %s, dt number: %s"%(m.get_zt_number(),m.get_dt_number()))
    #Get zixuan
    stock_status = "\n".join(m.util.get_summary_status(my_list))
    print(stock_status)

def check_zdt():
    m.check_top_and_bottom(30)

def check_zx():
    stock_status = "\n".join(m.util.get_summary_status(my_list))
    print(stock_status)

def check_stock(stock_id):
    stock_status = m.util.get_live_mon_items(stock_id)
    print(stock_status)

def check_fp_result():
    fp_list = db.get_fp_result()
    for fp in fp_list:
        print('=============')
        stock_list = fp.split(',')
        m.check_stock_list(stock_list)
        print('=============')
    pass

if __name__ == '__main__':       
    #monitor(file_name,60)
    #monitor_after_bid(file_name,60)
    while True:
        query_cmd = input("What?")
        try:
            if query_cmd=='zdt':
                check_zdt()
            elif query_cmd=='zx':
                check_zx()
            elif query_cmd=='fp':
                check_fp_result()
            elif query_cmd.startswith('sz') or query_cmd.startswith('sh'):
                check_stock(query_cmd)
        except:
            print("Please try again...")
    #send_sum_mail()