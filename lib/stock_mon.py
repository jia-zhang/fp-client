from stock_util import StockUtil
from logger import Logger
import time

class StockMon():
    def __init__(self):
        self.logger = Logger("StockMon")
        self.util = StockUtil()
        pass
    
    def monitor_bid(self,stock_list,refresh_interval):
        while True:
            self.logger.info("================Monitor==============")
            self.logger.info("股票名称（股票ID）| 涨幅 | 竞买价 | 竞买量")
            for s in stock_list:
                status = self.util.get_live_mon_items_bid(s)
                self.logger.info(status)    
            time.sleep(refresh_interval)

    def monitor_after_bid(self,stock_list,refresh_interval):
        while True:        
            self.logger.info("===============Monitor===============")
            self.logger.info("股票名称（股票ID）| 开盘涨幅 | 当前涨幅 | 当前价格 | 成交量（万手）| 成交金额（亿）")
            for s in stock_list:
                self.logger.info(self.util.get_live_mon_items(s))
            time.sleep(refresh_interval)

if __name__ == '__main__':
    t = StockMon()
    s_list = ['sz000002','sh600000']
    t.monitor_bid(s_list,5)
    #t.monitor_after_bid(s_list,5)