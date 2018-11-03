import os
import datetime
from logger import Logger

class StockTrade():    
    def __init__(self,trading_log):
        self.trading_log = trading_log
        self.logger = Logger("StockTrade")
        if not os.path.exists(trading_log):
            f = open(trading_log,"w")
            f.write(self._compose_trading_log("cash:1000000"))
            f.close()
    
    def _compose_trading_log(self,log_str):
        _now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        _log = "%s,%s"%(_now_time,log_str)
        return _log
    
    def append_trading_log(self,log_str):
        with open(self.trading_log,'a+') as f:
            c_log = self._compose_trading_log(log_str)
            f.write("\n")
            f.write(c_log)
    
    def get_last_trading_log(self):
        ret = ""
        with open(self.trading_log,'r') as f:
            output = f.readlines()
        for i in range(len(output)):
            ret = output[-1-i]
            if ret.startswith("201"):
                break
        #last_line = output[-1].replace("\n","")
        return ret.replace("\n","")

    def get_stock_holding(self,stock_id):
        ret = 0       
        items = self.get_last_trading_log().split(',')
        #print(stock_id)
        for i in range(len(items)):
            s = items[i]
            if not stock_id in s:
                continue
            return int(s.split(":")[-1])
        return ret
    
    def get_cash(self):
        ret = 0
        items = self.get_last_trading_log().split(',')
        for i in range(len(items)):
            s = items[i]
            if not "cash" in s:
                continue
            return int(s.split(":")[-1])
        return ret

    def buy(self,stock_id,stock_count,stock_price):
        last_log = ','.join(self.get_last_trading_log().split(',')[1:])
        cur_cash = self.get_cash()
        need_cash = stock_count*stock_price
        if cur_cash<need_cash:
            self.logger.info("Buy %s %s need %s money, you only have %s mondy, abort this..."%(stock_count,stock_id,need_cash,cur_cash))
            return -1
        new_cash = cur_cash-need_cash
        cur_holding = self.get_stock_holding(stock_id)
        if cur_holding!=0:
            new_holding = cur_holding + stock_count
            new_log = last_log.replace("cash:%s"%(cur_cash),"cash:%s"%(new_cash)).replace("%s:%s"%(stock_id,cur_holding),"%s:%s"%(stock_id,new_holding))
        else:
            new_log = "%s,%s:%s"%(last_log.replace("cash:%s"%(cur_cash),"cash:%s"%(new_cash)),stock_id,stock_count)
        self.append_trading_log(new_log)
        return new_log
    
    def sell(self,stock_id,stock_count,stock_price):
        last_log = ','.join(self.get_last_trading_log().split(',')[1:])
        cur_holding = self.get_stock_holding(stock_id)
        if cur_holding<stock_count:
            self.logger.info("Sell count(%s) is bigger then current holding(%s) stocks, abort this..."%(stock_count,cur_holding))
            return -1
        cur_cash = self.get_cash()
        new_cash = cur_cash+stock_price*stock_count
        new_holding = cur_holding - stock_count
        if new_holding != 0:
            new_log = last_log.replace("cash:%s"%(cur_cash),"cash:%s"%(new_cash)).replace("%s:%s"%(stock_id,cur_holding),"%s:%s"%(stock_id,new_holding))
        else:
            new_log = last_log.replace("cash:%s"%(cur_cash),"cash:%s"%(new_cash)).replace(",%s:%s"%(stock_id,cur_holding),"")
        self.append_trading_log(new_log)
        return new_log
    
    def buy_ratio(self,stock_id,ratio):
        pass
    
    def sell_ratio(self,stock_id,ratio):
        pass

if __name__ == '__main__':
    t = StockTrade("s1.log")
    #print(t.get_last_trading_log())
    #print(t.get_stock_holding('sz000001'))
    #print(t.get_cash())
    #print(t.sell('sz000001',100,20))
    print(t.buy("sz000002",500,10))