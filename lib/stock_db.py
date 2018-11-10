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
        sql_cmd = "insert into tb_fp_result values ('%s', '%s', '%s')"%(fp_date,fp_type,','.join(stock_list))
        self.update_db(sql_cmd)
    
    def get_fp_result(self,fp_date,fp_type):
        sql_cmd = "select stock_list from tb_fp_result where date='%s' and type='%s'"%(fp_date,fp_type)
        ret = self.query_db(sql_cmd)
        return ret[0][0]

    def get_last_dump_date(self):
        sql_cmd = "select date from tb_daily_info where stock_id='sh000001' order by date desc limit 1"
        ret = self.query_db(sql_cmd)
        return ret[0][0]

    def get_last_trading_date(self):
        sql_cmd = "select value from tb_configuration where name='last_trading_date'"
        ret = self.query_db(sql_cmd)
        return ret[0][0]
    
    def get_stock_basic(self,stock_id):
        sql_cmd = "select * from tb_basic_info where stock_id='%s'"%(stock_id)
        ret = self.query_db(sql_cmd)
        return ret[0]
    
    def get_stock_status(self,table_name,stock_id,day_n):
        '''
        day_n = 0 means last day
        day_n = 1 means the day before last day 
        No exception handling here(lazy...), please don't query day_n>15?
        '''
        sql_cmd = "select * from %s where stock_id='%s' order by date desc"%(table_name,stock_id)
        ret = self.query_db(sql_cmd)
        return ret[day_n]
    
    def get_stock_list(self):
        sql_cmd = "select * from tb_basic_info"
        ret = self.query_db(sql_cmd)
        #print(type(ret))
        return DataFrame(ret)[0].values.tolist()
    
if __name__ == '__main__':
    #print("hello")
    t = StockDb()
    '''
    stock_list = t.get_fp_result('2018-11-09','龙头').split(',')
    for s in stock_list:
        #print(s)
        #print(t.get_stock_name_from_id(s))
        print(t.get_stock_status(s,14))
    #print(t.get_last_trading_date())
    '''
    #s = 'sz000538'
    #print(t.get_stock_status(s,0))
    print(t.get_stock_list())


    
