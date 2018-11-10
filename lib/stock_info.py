import requests
import re
import time
import os
import json
import pdb
#from stock_util import StockUtil
from logger import Logger
from stock_db import StockDb

class StockInfo():
    def __init__(self,stock_id):
        self.stock_id = stock_id

    def stock_name(self):
        db = StockDb()
        basic_info = db.get_stock_basic(self.stock_id)
        return basic_info[1]
    
    def last_trading_date(self):
        db = StockDb()
        status = db.get_stock_status('tb_daily_info',self.stock_id,0)
        return status[0]
    
    def is_trading(self):
        db = StockDb()
        return db.get_last_trading_date()==self.last_trading_date()

if __name__ == '__main__':
    t = StockInfo('sz000538')
    print(t.is_trading())
