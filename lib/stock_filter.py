import requests
import re
import time
import datetime
import os
import json
import pdb
from stock_util import StockUtil
from stock_db import StockDb
from logger import Logger
from pandas import DataFrame

class StockFilter():
    def __init__(self):
        self.logger = Logger("StockFilter")
        self.db = StockDb()
        self.util = StockUtil()        

    def check_if_time_available(self):
        pass
    
    def get_top_increase(self,stock_list,n,day_num):
        d = {}
        for s in stock_list:
            d[s] = self.util.get_delta(s,day_num)
        sorted_list = sorted(d.items(), key=lambda d:d[1],reverse=True) 
        ret = []
        for i in range(1000):
            stock_id = sorted_list[i][0]
            ret.append(stock_id)
            if len(ret)==n:
                break
        return ret
    
    def filter_new_stocks(self,stock_list):
        new_stocks = self.db.get_new_stocks()
        return list(set(stock_list)-set(new_stocks))
    
    def get_volume_within_days(self,stock_list,day_num,volume_critiria):  
        '''
        过滤stock_list，返回day_num天前到现在，换手率超过volume_critiria的股票
        例如，get_volume_within_days(stock_list, 3, 20)表示返回3天内总换手超过20%的股票
        '''      
        ret = []
        for s in stock_list:
            volume = self.util.get_volume_sum(s,day_num)
            if volume>=volume_critiria:
                #self.logger.info("%s:%s"%(self.util.get_stock_name_from_id(s),volume))
                ret.append(s)
        self.logger.info("Found %s stocks after get volume sum within %s days"%(len(ret),day_num))
        return ret
    
    def get_delta_within_days(self,stock_list,day_num,delta_criteria):
        '''
        过滤stock_list，返回delta_day内涨幅>delta_critira的股票列表
        例如，get_delta_within_days(stock_list,3,20)表示拿到3天内涨幅>20%的股票列表
        '''
        self.logger.info("======Start, get delta>%s stocks within %s days...======"%(delta_criteria,day_num))
        ret=[]        
        for s in stock_list:
            delta = self.db.get_sum_n_pchg(s,day_num)
            #self.logger.info("%s:%s"%(s,delta))
            if(delta>delta_criteria and s not in ret):
                ret.append(s)
        filtered_list=list(set(stock_list)-set(ret))
        self.logger.info("Filtered %s stocks"%(len(filtered_list)))
        self.logger.info(filtered_list)
        self.logger.info("======End, found %s stocks======"%(len(ret)))        
        return ret
    
    def get_big_increase_within_days(self,stock_list,day_num,increase_criteria=9):
        self.logger.info("======Start, Get big increase within %s days======"%(day_num))
        day_list = self.db.get_last_n_dates(day_num)
        sql_cmd = "select distinct stock_id from tb_daily_info where pchg>%s and date>='%s' and pchg!=''"%(increase_criteria,day_list[-1]) 
        ret = self.db.query_db(sql_cmd)       
        match_list = DataFrame(ret)[0].values.tolist()
        ret = list(set(stock_list).intersection(set(match_list)))
        self.logger.info("======End, found %s stocks after calling get_big_increase_within_days======"%(len(ret)))
        return ret
    
    def get_big_turnover_within_days(self,stock_list,day_num,turnover_criteria=5):
        self.logger.info("======Start, get big turnover within %s days======"%(day_num))
        day_list = self.db.get_last_n_dates(day_num)
        sql_cmd = "select distinct stock_id from tb_daily_info where turnover>%s and date>='%s' and turnover!=''"%(turnover_criteria,day_list[-1]) 
        ret = self.db.query_db(sql_cmd)       
        match_list = DataFrame(ret)[0].values.tolist()
        ret = list(set(stock_list).intersection(set(match_list)))
        self.logger.info("======Start, found %s stocks after calling get_big_turnover_within_days======"%(len(ret)))
        return ret
    
    def filter_big_lift_within_days(self,stock_list,day_num,lift_criteria):
        '''
        过滤stock_list,如果在day_num内，出现大阴线形态2（高点和收盘差超过lift_critiria），则剔除这些股票。
        返回一个stock列表，去掉了所有n日内有大阴线形态2的股票。
        '''
        ret = []
        self.logger.info("======Start, filter big lift within %s days======"%(day_num))
        for s in stock_list:
            sum_lift = self.db.get_sum_n_lift(s,day_num)
            if sum_lift>lift_criteria:
                ret.append(s)
        filtered_list=list(set(stock_list)-set(ret))
        self.logger.info("Filtered %s stocks"%(len(filtered_list)))
        self.logger.info(filtered_list)
        self.logger.info("======End, found %s stocks after filtering big lift within %s days======"%(len(ret),day_num))
        return ret    

    def get_mkt_share_below_limit(self,stock_list,mkt_share_limit=100):
        #Get market share below 100E...
        ret = []
        self.logger.info("Get mkt share which is below %sE..."%(mkt_share_limit))
        for s in stock_list:
            float_shares = round(self.db.get_float_shares_from_id(s)/100000000,2)
            cur_price = float(self.util.get_live_status(s).split(',')[3])
            mkt_share = float_shares*cur_price
            if mkt_share<mkt_share_limit:
                #self.logger.info("Add stock %s which mkt share<%s"%(s,mkt_share_limit))
                ret.append(s)
        return ret

    def get_float_shares_below_limit(self,stock_list,float_shares_limit=10):
        ret = []
        match_list = self.db.get_stock_list_by_float_shares(float_shares_limit)
        ret = list(set(stock_list).intersection(set(match_list)))
        return ret
    
    def get_increase_rate_increase(self,stock_list,day_num,increase_criteria=1):
        self.logger.info("======Start, get increase rate increase within %s days======"%(day_num))
        ret = []        
        for s in stock_list: 
            try:            
                increase_list = self.db.get_last_n_pchg(s,day_num)           
                if increase_list!=[] and self.util.is_list_sorted(increase_list)=='desc':
                    #self.logger.info("Function get_increase_rate_increase, add stock %s"%(s))
                    ret.append(s)
            except:
                self.logger.info("Exception on stock:%s"%(s))
        self.logger.info("======End, Found %s stocks after filtering get_increase_rate_increase within %s days======"%(len(ret),day_num))
        return ret
    
    def get_turnover_increase(self,stock_list,day_num,increase_criteria=1):
        self.logger.info("Get volume rate increase within %s days"%(day_num))
        ret = []
        for s in stock_list: 
            turnover_list = self.db.get_last_n_turnover(s,day_num)           
            if self.util.is_list_sorted(turnover_list)=='desc':
                self.logger.info("Add stock %s"%(s))
                ret.append(s)
        self.logger.info("Found %s stocks after filtering get_turnover_increase within %s days"%(len(ret),day_num))
        return ret

    def get_turnover_burst(self,stock_list,day_num,increase_criteria=1):
        self.logger.info("Get volume rate increase within %s days"%(day_num))
        ret = []
        for s in stock_list: 
            turnover_list = self.db.get_last_n_turnover(s,day_num) 
            turnover_list.reverse()
            while len(turnover_list)>1:
                turnover = turnover_list.pop()
                average = sum(turnover_list)/len(turnover_list)
                #print("%s-%s:%s"%(s,turnover,average))
                if turnover/average>2:
                    ret.append(s)
                    self.logger.info("Add stock %s"%(s))   
                    break             
        self.logger.info("Found %s stocks after filtering get_turnover_burst within %s days"%(len(ret),day_num))
        return ret
    
    
    


if __name__ == '__main__':
    t = StockFilter()
    print(t.filter_new_stocks([]))
    
    