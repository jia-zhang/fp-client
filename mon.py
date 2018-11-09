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

if __name__ == '__main__':  
    mon()