# -*- coding: utf-8 -*-  
import requests
import re
import time
import os
from logger import Logger
from stock_db import StockDb
from stock_mon import StockMon
from pandas import DataFrame

class StockDump():
    def __init__(self,default_count=1):        
        self.logger = Logger("StockDump")        
        self.mon = StockMon()       
        self.default_count = default_count #if dump occurs everyday, it should only get the data of last trading date           
        self.pre_dump_file = 'predump.csv'
    
    def update_last_trading_date(self):
        sql_cmd = "update tb_configuration set value='%s' where name='last_trading_date'"%(self.last_trading_date)
        self.db.update_db(sql_cmd)

    def get_last_trading_date_live(self):        
        self.logger.info("Getting last trading date live...")
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=5&ma=no&datalen=5"
        resp = requests.get(detail_url)
        date = eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']   
        ret = date.split(' ')[0]
        self.logger.info("Last trading date is %s"%(ret))
        return ret

    def pre_dump(self):    
        self.logger.info('Starting pre-dump from sina...')    
        f = open(self.pre_dump_file,'w')
        mon = StockMon()
        for i in range(1,500):
            status = mon.get_market_status(0,i,100)
            if status == '':
                print('No data in this %s page, predump completed'%i)
                break
            else:            
                df = DataFrame(status)                
                df1 = df[['code','open','high','low','trade','volume','turnoverratio','changepercent']]    
                print(df1)
                df1.to_csv(f,header=False,index=False)
        f.close()   
        self.logger.info('Pre-dump from sina done...')
    
    def update_db(self):
        self.logger.info("Start store pre-dumped info to database...")
        db = StockDb('ss.db')
        total_stocks = db.get_stock_list()

        f = open(self.pre_dump_file,'r') 
        last_trading_date = self.get_last_trading_date_live()
        recorded_stocks = []
        no_data_stocks = []
        for line in f.readlines():
            item = line.replace('\n','').split(',')    
            if item[0].startswith('60'):
                stock_id = "sh%s"%(item[0])
            else:
                stock_id = "sz%s"%(item[0])
            recorded_stocks.append(stock_id)   
            if (item[1]=='0.000'):
                no_data_stocks.append(item[0])
                continue
            sql_cmd = "insert into tb_daily_info values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"\
            %(last_trading_date,stock_id,item[1],item[2],item[3],item[4],item[5],item[6],item[7])
            #db.update_db(sql_cmd)   
        f.close()   
        print('Total stock from db:%s,stocks from prelist:%s'%(len(total_stocks),len(recorded_stocks)))     
        test = []
        for s in total_stocks:
            if s not in recorded_stocks:
                test.append(s)
        print('===Stocks in total, but not in prelist====')
        print(test)
        test=[]
        for s in recorded_stocks:
            if s not in total_stocks:
                test.append(s)
        print('===Stocks in prelist,but not in total===')
        print(test)
        self.logger.info("There are total %s stock which have no data..."%(len(no_data_stocks)))
        self.logger.info("Store pre-dumped info to database done...")

if __name__ == '__main__':
    t = StockDump()
    #t.pre_dump()
    t.update_db()
    #t.pre_dump_mt(10)  
    #t.pre_dump_st()
    #date = '2018-11-13'
    #stock_id = 'sz000002'
    #print(t.pre_dump_today(stock_id))
    
   
    
    
  


