# -*- coding: utf-8 -*-  
import requests
import re
import time
import os
import json
import random
import datetime
import subprocess
import sys
from logger import Logger
from stock_util import StockUtil
from stock_db import StockDb
import threading

class StockDump():
    def __init__(self,default_count=1):        
        self.logger = Logger("StockDump")
        self.db = StockDb()              
        self.default_count = default_count #if dump occurs everyday, it should only get the data of last trading date           
        self.util = StockUtil()
    
    def update_last_trading_date(self):
        sql_cmd = "update tb_configuration set value='%s' where name='last_trading_date'"%(self.last_trading_date)
        self.db.update_db(sql_cmd)

    def get_last_trading_date_live(self):        
        self.logger.info("Getting last trading date live...")
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        resp = requests.get(detail_url)
        return eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']
    
    def get_stock_detail(self,stock_id,time_range,count,retry_num=3):        
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        ret = ''
        proxies = {'http': 'http://18.197.117.119:8080', 'https': 'http://18.197.117.119:8080'}
        detail_url = ("http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?"
                    "symbol=%s&scale=%s&ma=no&datalen=%s"
        )%(stock_id,time_range,count)        
        try:
            resp = requests.get(detail_url, proxies = proxies, timeout=60)
            #resp = requests.get(detail_url, timeout=60)
            if resp.status_code!=200:
                requests.raise_for_status()
            ret = resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"')\
            .replace('high','"high"').replace('close','"close"').replace('volume','"volume"')
        except requests.exceptions.ConnectionError as e:
            self.logger.info("Connection error...exit")
            return ret
        except:            
            if retry_num>0:            
                self.logger.info("Non 200 respose, retry. Status_code=%s"%(resp.status_code))
                return self.get_stock_detail(stock_id,time_range,count,retry_num-1)
        return ret 

    def get_pchg_turnover(self,stock_id,date): #get price change percent for one day
        ret = []
        ori_stock_id = stock_id
        if stock_id.startswith('sh'):
            stock_id = "0%s"%(stock_id.replace('sh',''))
        else:
            stock_id = "1%s"%(stock_id.replace('sz',''))
        date = date.replace('-','')
        proxies = {'http': 'http://18.197.117.119:8080', 'https': 'http://18.197.117.119:8080'}
        url = "http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s&fields=PCHG;TURNOVER"%(stock_id,date,date)
        #print(url)
        r = requests.get(url,proxies = proxies, timeout=60)
        #r = requests.get(url)
        #self.logger.info(r.text)
        r_list = r.text.split('\r\n')[1:-1]
        for line in r_list:
            tmp = line.split(',')
            date = tmp[0]
            pchg = round(float(tmp[-2]),2)
            turnover = round(float(tmp[-1]),2)
            ret.append(pchg)
            ret.append(turnover)
        return ret
    
    def get_pchg_turnover_today(self,stock_id):
        pass
    
    def check_pchg_ready(self,date):
        stock_id = 'sh000001'
        return self.get_pchg_turnover(stock_id,date)
    
    def dump_stock(self,stock_id,time_range,count):
        '''
        Will return a list of stock info get from sina...
        '''
        self.logger.info("Dump stock %s..."%(stock_id))
        tmp = self.get_stock_detail(stock_id,time_range,count)
        if tmp=='null':
            return []
        stock_detail_list = eval(tmp)
        return stock_detail_list
    
    def dump_stock_daily(self,stock_id):
        return self.dump_stock(stock_id,240,self.default_count)
    
    def dump_stock_weekly(self,stock_id):
        return self.dump_stock(stock_id,1680,self.default_count)
    
    def dump_stock_monthly(self,stock_id):
        return self.dump_stock(stock_id,7200,self.default_count)
    
    def pre_dump(self,stock_id):        
        f = open(self.pre_dump_file,'a')
        stock_detail_list = self.dump_stock_daily(stock_id)
        if stock_detail_list==[]:
            f.close()
            return
        for stock_detail in stock_detail_list:
            combined_info = self.combine_stock_info(stock_id,stock_detail)
            f.write("%s\n"%(combined_info))
        f.close()
    
    def combine_stock_info(self,stock_id,stock_detail_dict):
        date = stock_detail_dict['day']
        price_open = stock_detail_dict['open']
        price_high = stock_detail_dict['high']
        price_low = stock_detail_dict['low']
        price_close = stock_detail_dict['close']
        volume = stock_detail_dict['volume']
        if(stock_id=='sh000001'):
            pchg_turnover = ['','']
        else:
            pchg_turnover = self.get_pchg_turnover(stock_id,date)
        #float_shares = self.db.get_float_shares_from_id(stock_id)
        turn_over = pchg_turnover[1]
        p_chg = pchg_turnover[0]
        ret = "%s,%s,%s,%s,%s,%s,%s,%s,%s"%(date,stock_id,price_open,price_high,price_low,price_close,volume,turn_over,p_chg)
        return ret

    def pre_dump_today(self,stock_id):
        self.logger.info("Dump stock %s..."%(stock_id))
        f = open(self.pre_dump_file,'a')
        live_status = self.util.get_live_status(stock_id).split(',')
        cur_price = float(live_status[3])
        last_day_price = float(live_status[2])        
        date = live_status[30]
        price_open = live_status[1]
        price_high = live_status[4]
        price_low = live_status[5]
        price_close = live_status[3]
        volume = live_status[8]
        #float_shares = self.db.get_float_shares_from_id(stock_id)
        float_shares = self.float_shares_dict[stock_id]
        turn_over = round(float(volume)*100/float_shares,2)
        p_chg = round((cur_price-last_day_price)*100/last_day_price,2) 
        all_combined = "%s,%s,%s,%s,%s,%s,%s,%s,%s"%(date,stock_id,price_open,price_high,price_low,price_close,volume,turn_over,p_chg)
        f.write("%s\n"%(all_combined))
        f.close()
        #print(all_combined)
    
    def pre_dump_st(self):
        self.stock_list = self.db.get_stock_list()  
        self.last_trading_date = self.get_last_trading_date_live()
        self.pre_dump_file = "predump-%s.csv"%(self.last_trading_date)
        self.logger.info("Last trading date is %s"%(self.last_trading_date))
        self.float_shares_dict = self.db.get_float_shares_dict()
        for s in self.stock_list:
            self.pre_dump_today(s)

    def pre_dump_mt(self,thread_num):
        self.stock_list = self.db.get_stock_list()  
        self.last_trading_date = self.get_last_trading_date_live()
        self.pre_dump_file = "predump-%s.csv"%(self.last_trading_date)
        self.logger.info("Last trading date is %s"%(self.last_trading_date))
        #self.float_shares_dict = self.db.get_float_shares_dict()
        threads = []
        for s in self.stock_list:
            #t=threading.Thread(target=self.pre_dump_today,args=(s,))
            t=threading.Thread(target=self.pre_dump,args=(s,))
            threads.append(t)
        for t in threads:
            t.start()
            while True:
                if(len(threading.enumerate())<thread_num):
                    break

    def update_db(self):
        f = open('predump-2018-11-13.csv','r') 
        download_list = []
        for line in f.readlines():
            item = line.replace('\n','').split(',')            
            if (item[0]!='2018-11-13'):
                continue
            sql_cmd = "insert into tb_daily_info values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"\
            %(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8])
            t.db.update_db(sql_cmd)    
        f.close()
    
    def check_data_readiness(self):
        found_sina = 0
        found_163 = 0
        while True:
            if found_sina==1 and found_163==1:
                break
            if found_sina==0:
                trading_date = t.get_last_trading_date_live()
                if trading_date == date:
                    t.logger.info("Found sina")
                    found_sina = 1
            if found_163==0:
                pchg = t.get_pchg_turnover(stock_id,date)
                if pchg!=[]:
                    t.logger.info("Found 163")
                    found_163 = 1
            t.logger.info("Found sina:%s,Found 163:%s"%(found_sina,found_163))
            time.sleep(10)

if __name__ == '__main__':
    t = StockDump()
    t.update_db()
    #t.pre_dump_mt(10)  
    #t.pre_dump_st()
    #date = '2018-11-13'
    #stock_id = 'sz000002'
    #print(t.pre_dump_today(stock_id))
    
   
    
    
  


