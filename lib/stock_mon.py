from stock_util import StockUtil
from logger import Logger
from stock_db import StockDb
import time
import threading

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
        self.logger.info("================Monitor==============")
        self.logger.info("  股票名称（股票ID）       | 开盘涨幅  | 当前涨幅  | 当前价格 |    成交量      |   成交金额   | 昨日换手 | 昨日涨幅  |    流通股")            
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

    def check_fp_list(self):
        db = StockDb()
        fp_types = ['龙头','潜力','屌丝潜力']        
        date = db.get_last_trading_date()
        for t in fp_types:
            s_list = db.get_fp_result(date,t).split(',')
            self.check_stock_list(s_list)        

if __name__ == '__main__':
    t = StockMon()
    t.check_fp_list()
    '''
    db = StockDb()
    s_list = []
    sql_cmd = "select stock_list from tb_fp_result where type='龙头'"    
    lt = list(db.query_db(sql_cmd)[0])[0].split(',')
    print(type(lt))
    print(lt)
    sql_cmd = "select stock_list from tb_fp_result where type='潜力'"  
    ql = list(db.query_db(sql_cmd)[0])[0].split(',')
    sql_cmd = "select stock_list from tb_fp_result where type='屌丝潜力'"  
    ds = list(db.query_db(sql_cmd)[0])[0].split(',')
    #print(list(lt[0]))
    t.check_stock_list(lt)
    t.check_stock_list(ql)
    t.check_stock_list(ds)
    
    s_list.append(lt)
    s_list.append(ql)
    s_list.append(ds)
    threads = [threading.Thread(target=t.monitor_bid, args=(s, )) for s in s_list]
    for t in threads:
        t.start()  #启动一个线程
    for t in threads:
        t.join()  #等待每个线程执行结束
    '''

    