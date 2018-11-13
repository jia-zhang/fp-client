import requests
import re
import time
import os
import json
import pdb
from stock_util import StockUtil
from stock_db import StockDb
from logger import Logger
from pandas import DataFrame

class StockFilter():
    def __init__(self):
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        #detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        #resp = requests.get(detail_url)
        self.logger = Logger("StockFilter")
        self.db = StockDb()
        self.util = StockUtil()
        #self.last_trading_day = eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        #replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']

    def check_if_time_available(self):
        pass
    
    def get_top_increase(self,stock_list,n,day_num):
        d = {}
        for s in stock_list:
            d[s] = self.util.get_delta(s,day_num)
        #print(d)
        sorted_list = sorted(d.items(), key=lambda d:d[1],reverse=True) 
        #print(sorted_list)
        ret = []
        for i in range(n):
            ret.append(sorted_list[i][0])
        return ret
    
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
        self.logger.info("Start, get delta>%s stocks..."%(delta_criteria))
        ret=[]
        for s in stock_list:
            delta = self.util.get_delta(s,day_num)
            #self.logger.info("%s:%s"%(s,delta))
            if(delta>delta_criteria and s not in ret):
                ret.append(s)
        self.logger.info("End, found %s stocks"%(len(ret)))
        self.logger.info("============================\n\n")
        return ret
    
    def get_big_increase_within_days(self,stock_list,day_num,increase_criteria):
        '''
        Done
        '''
        self.logger.info("Filter big increase within %s days"%(day_num))
        day_list = self.db.get_last_n_dates(day_num)
        #print(day_list)
        sql_cmd = "select distinct stock_id from tb_daily_info where pchg>%s and date>='%s' and pchg!=''"%(increase_criteria,day_list[-1]) 
        #print(sql_cmd)
        ret = self.db.query_db(sql_cmd)       
        return DataFrame(ret)[0].values.tolist()
    
    def filter_big_lift_within_days(self,stock_list,day_num,lift_criteria):
        '''
        过滤stock_list,如果在day_num内，出现大阴线形态2（高点和收盘差超过lift_critiria），则剔除这些股票。
        返回一个stock列表，去掉了所有n日内有大阴线形态2的股票。
        '''
        tmp = []
        self.logger.info("Filter big lift within %s days"%(day_num))
        #print(stock_list)
        for s in stock_list:
            #self.logger.info(s)
            for day in range(day_num):
                lift = self.util.get_lift_in_one_day(s,day)
                #self.logger.info("%s:%s"%(s,drop))
                if lift<lift_criteria:
                    #pdb.set_trace()
                    self.logger.info("Remove stock %s big lift>criteria...Lift day: %s"%(s,day))
                    tmp.append(s)
                    break
        ret = list(set(stock_list) ^ set(tmp))
        self.logger.info("Found %s stocks after filtering big lift within %s days"%(len(ret),day_num))
        return ret
    
    def filter_big_drop_within_days(self,stock_list,day_num,drop_criteria):
        '''
        过滤stock_list,如果在day_num内，出现大阴线（下跌超过drop_critiria），则剔除这些股票。
        返回一个stock列表，去掉了所有n日内有大阴线的股票。
        '''
        tmp = []
        self.logger.info("Filter big drop within %s days"%(day_num))
        #print(stock_list)
        for s in stock_list:
            #self.logger.info(s)
            for day in range(day_num):
                drop = self.util.get_increase_amount(s,day)
                #self.logger.info("%s:%s"%(s,drop))
                if drop<drop_criteria:
                    #pdb.set_trace()
                    self.logger.info("Remove stock %s big drop>criteria...Drop day: %s"%(s,day))
                    tmp.append(s)
                    break
        ret = list(set(stock_list) ^ set(tmp))
        self.logger.info("Found %s stocks after filtering big drop within %s days"%(len(ret),day_num))
        return ret
    
    def get_increase_rate_increase(self,stock_list,day_num,increase_criteria=1):
        self.logger.info("Get increase rate increase within %s days"%(day_num))
        ret = []
        for s in stock_list: 
            increase_list = self.db.get_last_n_pchg(s,day_num)           
            if self.util.is_list_sorted(increase_list)=='desc':
                self.logger.info("Add stock %s"%(s))
                ret.append(s)
        self.logger.info("Found %s stocks after filtering get_increase_rate_increase within %s days"%(len(ret),day_num))
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
    s_list = t.db.get_trading_stock_list()
    
    s_list = t.get_big_increase_within_days(s_list,5,9)
    print(s_list)
    
    