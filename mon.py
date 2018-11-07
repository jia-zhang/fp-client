import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil
import time

def monitor(file_name,refresh_interval):
    t = StockUtil()
    s_list = t.get_stock_list_from_file(file_name)
    #s_list_str = ','.join(s_list)
    #print(s_list)
    while True:
        t.logger.info("================Monitor==============")
        t.logger.info("股票名称、昨日收盘价、竞买价、竞卖价、买1手、买1报价、卖1手、卖5报价、日期、时间")
        #for s in s_list:
        status = t.get_live_status_list(s_list).replace(",0.000",'').replace(',0','')
        print(status)    
        time.sleep(refresh_interval)
    pass

def monitor_after_bid(file_name,refresh_interval):
    t = StockUtil()
    s_list = t.get_stock_list_from_file(file_name)
    while True:        
        t.logger.info("===============Monitor===============")
        t.logger.info("股票ID，股票名称，当前价格，涨幅，成交手数，成交金额，开盘涨幅")
        for s in s_list:
            t.logger.info(t.get_live_mon_items(s))
        time.sleep(refresh_interval)


if __name__ == '__main__':   
    file_name = 'output/2018_11_06.csv'
    #monitor(file_name,60)
    monitor_after_bid(file_name,60)