import requests
import re
import time
import os
import json
import pdb
#from stock_util import StockUtil
from logger import Logger
import sqlite3
from pandas import DataFrame

class StockDb():
    def __init__(self,db_name='ss.db'):
        self.db_name = db_name        
        self.logger = Logger("StockDb")
        #self.util = StockUtil()    
    
    def update_db(self,sql_cmd):
        self.conn = sqlite3.connect(self.db_name)
        cur = self.conn.cursor()
        cur.execute(sql_cmd)
        self.conn.commit()
        self.conn.close()

    def query_db(self,sql_cmd):
        self.conn = sqlite3.connect(self.db_name)
        cur = self.conn.cursor()
        cur.execute(sql_cmd)
        res = cur.fetchall()
        self.conn.close()
        return res
    
    def add_fp_result(self,stock_list,fp_type,fp_date):
        sql_cmd = "insert into tb_fp_result values ('%s', %s, '%s')"%(fp_date,fp_type,','.join(stock_list))
        print(sql_cmd)
        self.update_db(sql_cmd)
    
    def get_fp_result(self,fp_date,fp_type):
        sql_cmd = "select stock_list from tb_fp_result where date='%s' and type=%s"%(fp_date,fp_type)
        ret = self.query_db(sql_cmd)
        return ret[0][0]  
    
    '''
    def get_last_dump_date(self):
        sql_cmd = "select date from tb_daily_info where stock_id='sh000001' order by date desc limit 1"
        ret = self.query_db(sql_cmd)
        return ret[0][0]
    '''

    def get_stock_list_by_float_shares(self,float_shares_limit):
        sql_cmd = "select stock_id from tb_basic_info where float_shares<%s"%(float_shares_limit*100000000)
        ret = self.query_db(sql_cmd)
        return DataFrame(ret)[0].values.tolist()

    def get_last_trading_date(self):
        sql_cmd = "select value from tb_configuration where name='last_trading_date'"
        ret = self.query_db(sql_cmd)
        return ret[0][0]
    
    def get_stock_basic(self,stock_id):
        '''
        Return emtpy list if the stock_id is not in tb_basic_info table.
        '''
        sql_cmd = "select * from tb_basic_info where stock_id='%s'"%(stock_id)
        ret = self.query_db(sql_cmd)
        return ret
    
    def get_turnover_by_daynum(self,stock_id,day_n):
        return self.get_stock_status(stock_id,day_n)[7]
    
    def get_pchg_by_daynum(self,stock_id,day_n):
        return self.get_stock_status(stock_id,day_n)[8]
    
    def get_stock_name_from_id(self,stock_id):
        return self.get_stock_basic(stock_id)[0][1]
    
    def get_float_shares_from_id(self,stock_id):
        return self.get_stock_basic(stock_id)[0][2]

    def get_in_mkt_date_from_id(self,stock_id):
        ret = self.get_stock_basic(stock_id)[0][3]
        if ret==None:
            ret = '1999-01-01'
        return ret
    
    def get_stock_status(self,stock_id,day_n):
        '''
        day_n = 0 means last day
        day_n = 1 means the day before last day 
        No exception handling here(lazy...), please don't query day_n>15?
        '''
        sql_cmd = "select * from tb_daily_info where stock_id='%s' order by date desc"%(stock_id)
        ret = self.query_db(sql_cmd)
        return ret[day_n]
    
    def get_stock_list(self):
        sql_cmd = "select * from tb_basic_info"
        ret = self.query_db(sql_cmd)
        return DataFrame(ret)[0].values.tolist()
    
    def get_trading_stock_list(self):
        last_trading_date = self.get_last_trading_date()
        sql_cmd = "select * from tb_daily_info where date='%s'"%(last_trading_date)
        ret = self.query_db(sql_cmd)
        return DataFrame(ret)[1].values.tolist()
    
    def get_suspend_stock_list(self):
        all_stocks = self.get_stock_list()
        trading_stocks = self.get_trading_stock_list()
        return list(set(all_stocks) ^ set(trading_stocks))

    def get_rcpt_list(self):
        sql_cmd = "select value from tb_configuration where name='rcpt_list'"
        ret = self.query_db(sql_cmd)
        return ret[0][0].split(',')
    
    def get_last_n_dates(self,n):
        sql_cmd = "select date from tb_daily_info where stock_id='sh000001' order by date desc limit %s"%(n)
        ret = self.query_db(sql_cmd)
        return DataFrame(ret)[0].values.tolist()
    

    def get_last_n_pchg(self,stock_id, n):
        sql_cmd = "select pchg from tb_daily_info where stock_id='%s' order by date desc limit %s"%(stock_id,n)
        ret = self.query_db(sql_cmd)
        return DataFrame(ret)[0].values.tolist()

    def get_sum_n_pchg(self,stock_id,n):
        sql_cmd = "select sum(pchg) as total_pchg from (select * from tb_daily_info where stock_id='%s' order by date desc limit %s)"%(stock_id,n)
        ret = self.query_db(sql_cmd)
        return ret[0][0]
    
    def get_sum_n_lift(self,stock_id,n):
        sql_cmd = "select sum(lift) from (select *,((close-high)*100/close+(close-open)*100/open)/2 as lift \
        from tb_daily_info where stock_id='%s' order by date desc limit %s)"%(stock_id,n)
        ret = self.query_db(sql_cmd)
        return ret[0][0]
    
    def get_sum_n_turnover(self,stock_id,n):
        sql_cmd = "select sum(turnover) as total_turnover from (select * from tb_daily_info where stock_id='%s' order by date desc limit %s)"%(stock_id,n)
        ret = self.query_db(sql_cmd)
        return ret[0][0]
    
    def get_last_n_lift(self,stock_id,n):
        sql_cmd = "select lift from (select *,((close-high)*100/close+(close-open)*100/open)/2 as lift \
        from tb_daily_info where stock_id='%s' order by date desc limit %s)"%(stock_id,n)
        ret = self.query_db(sql_cmd)
        return ret
        

    def get_last_n_turnover(self,stock_id, n):
        sql_cmd = "select turnover from tb_daily_info where stock_id='%s' order by date desc limit %s"%(stock_id,n)
        ret = self.query_db(sql_cmd)
        return DataFrame(ret)[0].values.tolist()

    def get_float_shares_dict(self):
        sql_cmd = "select stock_id,float_shares from tb_basic_info"
        ret = self.query_db(sql_cmd)
        df = DataFrame(ret)
        stock_id_list = df[0].values.tolist()
        float_share_list = df[1].values.tolist()
        ret_dict = dict(zip(stock_id_list,float_share_list))
        return ret_dict
    
if __name__ == '__main__':
    #print("hello")
    t = StockDb()
    #fp_list = t.get_all_fp_result('2018-11-14')
    print(t.get_stock_list_by_float_shares(2))
    #print(fp_list)
    #print(t.get_turnover_by_daynum('sz000002',1))
    #print(t.get_pchg_by_daynum('sz000002',1))
    #print(t.get_turnover_by_daynum('sz00002',0))
    #print(t.get_sum_n_lift('sh600530',7))
    #print(t.get_in_mkt_date_from_id('sz000002'))
    #print(t.get_in_mkt_date_from_id('sz300571'))
    #print(df)
    #print(df[0].values.tolist()[0:100])
    #print(df[1].values.tolist()[0:100])
    #print(s_list)
    #print(t.get_rcpt_list())
    #print(t.get_rcpt_list())
    #t.add_pre_dump_daily('2018-11-12')
    #print(t.get_last_turnover('sz000002'))
        #time.sleep(1)
    #stock_list = t.get_fp_result('2018-11-09',0).split(',')
    #print(stock_list)
    '''
    stock_list = t.get_fp_result('2018-11-09','龙头').split(',')
    for s in stock_list:
        #print(s)
        #print(t.get_stock_name_from_id(s))
        print(t.get_stock_status(s,14))
    #print(t.get_last_trading_date())
    '''
    #s = 'sz002940'
    
    #print(t.get_stock_list())
    '''
    s_list = t.get_suspend_stock_list()
    for s in s_list:
        #print(s)
        print(t.get_stock_name_from_id(s))
        #print(t.get_stock_status(s,14))
    '''
    



    
