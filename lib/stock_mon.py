from stock_util import StockUtil
from logger import Logger
import time

class StockMon():
    def __init__(self):
        self.logger = Logger("StockMon")
        self.util = StockUtil()
        pass
    
    def monitor_bid(self,stock_list,refresh_interval):
        sample = {}
        for s in stock_list:
            aoi = self.util.get_live_aoi_bid(s)
            sample[s] = aoi
        while True:
            self.logger.info("================Monitor==============")
            self.logger.info("股票名称（股票ID）| 涨幅 | 竞买价 | 竞买量（万手）")            
            for s in stock_list:
                status = self.util.get_live_mon_items_bid(s)
                aoi = self.util.get_live_aoi_bid(s)   
                if aoi-sample[s]>1:
                    plus_icon = "[↑+%s]"%(round(aoi-sample[s],2))
                    self.logger.info("*%s %s"%(status,plus_icon))
                elif aoi-sample[s]<-1:
                    plus_icon = "[↓%s]"%(round(aoi-sample[s],2))
                    self.logger.info("*%s %s"%(status,plus_icon))
                else:
                    self.logger.info(status) 
                '''               
                if aoi-sample[s]>2:
                    self.logger.info("Stock %s aoi increased from %s to %s"%(s,sample[s],aoi))
                elif aoi-sample[s]<-2:
                    self.logger.info("Stock %s aoi dropped from %s to %s"%(s,sample[s],aoi))
                '''
                sample[s] = aoi
            time.sleep(refresh_interval)

    def check_stock_list(self,stock_list):
        sample = {}        
        self.logger.info("================Monitor==============")
        self.logger.info("股票名称（股票ID）| 开盘涨幅 | 当前涨幅 | 当前价格 | 成交量（万手）| 成交金额（亿）")            
        for s in stock_list:
            status = self.util.get_live_mon_items(s)  
            self.logger.info(status)        


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
    t.monitor_bid(s_list,20)
    #t.monitor_after_bid(s_list,5)