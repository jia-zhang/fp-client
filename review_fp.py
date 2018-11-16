import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil
from stock_mon import StockMon
from stock_db import StockDb
import time


def check(stock_list):
    m = StockMon()
    m.check_stock_list(stock_list)

def review_fp(date):
    db = StockDb()
    for i in range(3):
        #print(i)
        s_list = db.get_fp_result(date,i)
        check(s_list.split(','))


if __name__ == '__main__': 
    review_fp('2018-11-15')