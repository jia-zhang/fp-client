import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil
from stock_mon import StockMon
import time

def mon():
    m = StockMon()
    s_list = m.util.get_fp_stock_list()
    m.monitor_bid(s_list,5)

if __name__ == '__main__':  
    mon()