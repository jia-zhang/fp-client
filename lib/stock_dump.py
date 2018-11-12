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
    def __init__(self):
        #self.stock_list_url = "http://quote.eastmoney.com/stocklist.html"
        self.logger = Logger("StockDump")
        self.db = StockDb('ss1.db')
        self.stock_list = self.db.get_stock_list()
        self.last_dump_date = self.db.get_last_dump_date()
        self.default_count = 1 #if dump occurs everyday, it should only get the data of last trading date   
        #self.last_trading_date = self.get_last_trading_date_live()        

    def get_last_trading_date_live(self):
        '''
        获取最近一次的交易日。获取上证指数的最后交易数据即可。
        '''
        self.logger.info("Getting last trading date live...")
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        resp = requests.get(detail_url)
        return eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']
    
    def get_stock_detail(self,stock_id,time_range,count,retry_num=3):
        '''
        获取某股票在time_range内的动态数据，开盘价，收盘价之类。
        统一从新浪拿，每天15：00以后拿一次就可以。
        '''
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        ret = ''
        #proxies = {'http': 'http://18.197.117.119:8080', 'https': 'http://18.197.117.119:8080'}
        detail_url = ("http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?"
                    "symbol=%s&scale=%s&ma=no&datalen=%s"
        )%(stock_id,time_range,count)
        #self.logger.info(detail_url)
        try:
            resp = requests.get(detail_url, timeout=60)
            if resp.status_code!=200:
                requests.raise_for_status()
            ret = resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"')\
            .replace('high','"high"').replace('close','"close"').replace('volume','"volume"')
        except requests.exceptions.ConnectionError as e:
            self.logger.info("Connection error...exit")
            return ret
        except:
            #html=None
            if retry_num>0:
            #如果不是200就重试，每次递减重试次数
                self.logger.info("Non 200 respose, retry. Status_code=%s"%(resp.status_code))
                return self.get_stock_detail(url,stock_id,time_range,count,retry_num-1)
        return ret 

    def get_pchg(self,stock_id,date): #get price change percent for one day
        ret = 0
        ori_stock_id = stock_id
        if stock_id.startswith('sh'):
            stock_id = "0%s"%(stock_id.replace('sh',''))
        else:
            stock_id = "1%s"%(stock_id.replace('sz',''))
        date = date.replace('-','')
        #proxies = {'http': 'http://18.197.117.119:8080', 'https': 'http://18.197.117.119:8080'}
        url = "http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s&fields=PCHG"%(stock_id,date,date)
        #print(url)
        r = requests.get(url)
        r_list = r.text.split('\r\n')[1:-1]
        for line in r_list:
            tmp = line.split(',')
            date = tmp[0]
            pchg = round(float(tmp[-1]),2)
            ret = pchg
        return ret
    
    '''
    def pre_dump(self,stock_list=[]):
        pre_dump_file = "predump-%s.csv"%(self.last_dump_date)
        f = open(pre_dump_file,'w')
        if stock_list==[]:
            stock_list = self.stock_list
        for stock_id in stock_list:
            stock_detail_list = self.dump_stock_daily(stock_id)
            combined_info = self.combine_stock_info(stock_id,stock_detail_list[0])
            f.write("%s\n"%(combined_info))
        f.close()
    '''
    
    def pre_dump(self,stock_id):
        pre_dump_file = "predump-%s.csv"%(self.last_dump_date)
        f = open(pre_dump_file,'a')
        stock_detail_list = self.dump_stock_daily(stock_id)
        combined_info = self.combine_stock_info(stock_id,stock_detail_list[0])
        f.write("%s\n"%(combined_info))
        f.close()

    def real_pre_dump(self):
        while True:
            try:
                stock_id = self.stock_list.pop()
            except IndexError:
                break
            self.pre_dump(stock_id)

    def pre_dump_mt(self,thread_num):
        for i in range(thread_num):
            t=threading.Thread(target=self.real_pre_dump())
            t.start()
        for i in range(thread_num):
            t.join()

    def combine_stock_info(self,stock_id,stock_detail_dict):
        date = stock_detail_dict['day']
        price_open = stock_detail_dict['open']
        price_high = stock_detail_dict['high']
        price_low = stock_detail_dict['low']
        price_close = stock_detail_dict['close']
        volume = stock_detail_dict['volume']
        float_shares = self.db.get_float_shares_from_id(stock_id)
        turn_over = round(float(volume)*100/float_shares,2)
        p_chg = self.get_pchg(stock_id,date)
        ret = "%s,%s,%s,%s,%s,%s,%s,%s,%s"%(date,stock_id,price_open,price_high,price_low,price_close,volume,turn_over,p_chg)
        return ret

       
    def update_db(self,stock_id,stock_detail_dict):
        date = stock_detail_dict['day']
        price_open = stock_detail_dict['open']
        price_high = stock_detail_dict['high']
        price_low = stock_detail_dict['low']
        price_close = stock_detail_dict['close']
        volume = stock_detail_dict['volume']
        float_shares = self.db.get_float_shares_from_id(stock_id)
        turn_over = round(float(volume)*100/float_shares,2)
        p_chg = self.get_pchg(stock_id,date)
        sql_cmd = "insert into tb_daily_info values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"\
        %(date,stock_id,price_open,price_high,price_low,price_close,volume,turn_over,p_chg)
        self.db.update_db(sql_cmd)
    
    def update_db_from_list(self,stock_id,stock_detail_list):
        for s_dict in stock_detail_list:
            self.update_db(stock_id,s_dict)

    def dump_stock(self,stock_id,time_range,count):
        '''
        Will return a list of stock info get from sina...
        '''
        dump_type = 'daily'
        self.logger.info("Dump stock %s..."%(stock_id))
        #file_name = self.util.get_dynamic_file_from_id(stock_id,dump_type)
        stock_detail_list = eval(self.get_stock_detail(stock_id,time_range,count))
        return stock_detail_list
    
    def dump_stock_daily(self,stock_id):
        return self.dump_stock(stock_id,240,self.default_count)
    
    def dump_stock_weekly(self):
        return self.dump_stock(stock_id,1680,self.default_count)
    
    def dump_stock_monthly(self):
        return self.dump_stock(stock_id,7200,self.default_count)

    
    def real_dump(self):
        while True:
            try:
                stock_id = self.stock_list.pop()
            except IndexError:
                break
            stock_detail_list = self.dump_stock_daily(stock_id)
            self.update_db_from_list(stock_id,stock_detail_list)

    def dump_stock_daily_mt(self):
        for i in range(10):
            t=threading.Thread(target=self.real_dump())
            t.start()
        for i in range(10):
            t.join()
    
    def dump_stock_daily_st(self):
        for stock_id in self.stock_list:
            stock_detail_list = self.dump_stock_daily(stock_id)
            self.update_db_from_list(stock_id,stock_detail_list)

    
    def dump_stock_dynamic(self,time_range,count,force=1):
        '''
        Dump stock info from sina.
        time_range = 240, 1680, 7200 - daily, weekly, monthly
        count = number of data need to  be dumpped        
        '''  
        self.logger.info(self.util.get_last_trading_date())
        s_list = self.util.get_valid_stocks()
        if time_range == 240:
            dump_type = 'daily'
        elif time_range == 1680:
            dump_type = 'weekly'
        elif time_range == 7200:
            dump_type = 'monthly'
        for s in s_list:
            self.logger.info("Dumping stock %s dynamic %s..."%(s,dump_type))
            #file_name = self.util.get_dynamic_file_from_id(s)
            file_name = self.util.get_dynamic_file_from_id(s,dump_type)
            #self.logger.info(file_name)
            if (force==0 and os.path.exists(file_name)):
                self.logger.info("%s already exists, skip"%(s))
                continue
            stock_detail = self.get_stock_detail(s,time_range,count)
            with open(file_name,'w') as f:
                f.write(stock_detail)
            
    def dump_stock_static(self,force=0): #Decrypted, remove it later
        '''
        Get some very basic static information from xueqiu.com
        if force==1, will overwrite exists json file, please be careful
        '''
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        re_fload_shares = re.compile(r'"float_shares":(\d*?),')
        re_stock_name = re.compile(r'"name":(.*?),')
        re_market_capital = re.compile(r'"market_capital":(.*?),')
        s_list = self.util.get_valid_stocks()
        for s in s_list:
            self.logger.info("Dumping stock static %s..."%(s))
            file_name = self.util.get_static_file_from_id(s)
            if (force==0 and os.path.exists(file_name)):
                self.logger.info("%s already exists, skip"%(s))
                continue
            try:
                master_dict = {}
                resp = requests.get("https://xueqiu.com/S/%s"%(s),headers=headers)
                if (resp.status_code==404):
                    self.logger.info("Get code 404 on stock %s"%(s))                    
                    continue
                elif(resp.status_code!=200):
                    self.logger.info("Get code %s on stock %s"%(resp.status_code,s))
                    continue
                resp.encoding = 'utf-8'            
                stock_dict = {}
                stock_dict['float_shares'] = str(re_fload_shares.findall(resp.text)[0])  
                stock_dict['stock_name'] = str(re_stock_name.findall(resp.text)[0])
                stock_dict['market_capital'] = str(re_market_capital.findall(resp.text)[0])
                master_dict[s] = stock_dict
                with open(file_name,'w') as f:
                    f.write(json.dumps(master_dict))
            except:
                self.logger.info("exception on stock %s!"%(s))
    
    

if __name__ == '__main__':
    t = StockDump()
    t.pre_dump_mt(10)
    #t.dump_stock_daily_st()
    #t.dump_stock_daily_mt()
    '''
    stock_id = 'sz000002'
    stock_detail_list = t.dump_stock_daily(stock_id)
    print(t.combine_stock_info(stock_id,stock_detail_list[0]))
    '''
    #stock_list = ['sz000002','sh600000']
    '''
    fp_types = ['龙头','潜力','屌丝潜力']        
    date = t.db.get_last_trading_date()
    for tp in fp_types:
        s_list = t.db.get_fp_result(date,tp).split(',')        
        t.pre_dump(s_list)
    '''
    #print(stock_detail)
    #print(t.get_pchg(stock_id,'2018-11-09'))
  


