import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil
from stock_mon import StockMon
import time

def mon():
    m = StockMon()
    s_list = m.util.get_fp_stock_list()
    if m.util.is_bid_time():
        m.logger.info("集合竞价时间：")
        m.monitor_bid(s_list,20)
    elif m.util.is_trading_time():
        m.logger.info("交易时间：")
        m.monitor_after_bid(s_list,20)
    else:
        m.logger.info("非交易时间，请等会再来！")

def check(stock_list):
    m = StockMon()
    m.check_stock_list(stock_list)

if __name__ == '__main__': 
    arg_len = len(sys.argv)
    if arg_len==1:
        mon()
    else:
        file_name = sys.argv[1]
        #print(file_name)
        t = StockUtil()
        stock_list = t.get_stock_list_from_file(file_name)
        #print(stock_list)
        check(stock_list)