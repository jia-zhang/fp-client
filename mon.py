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
        m.logger.info("Bid time...")
        m.monitor_bid(s_list,20)
    elif m.util.is_trading_time():
        m.logger.info("Trading time...")
        m.monitor_after_bid(s_list,20)

if __name__ == '__main__':  
    mon()