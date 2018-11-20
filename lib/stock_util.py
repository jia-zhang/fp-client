import requests
import re
import time
import os
import json
from logger import Logger
import datetime
from bs4 import BeautifulSoup
from stock_db import StockDb
from stock_info import StockInfo

class StockUtil():
    def __init__(self):
        self.logger = Logger("StockUtil")
        self.db = StockDb()
        self.valid_stock_file = "valid_stock.csv"
        pass

    def is_list_sorted(self,lst):
        if sorted(lst) == lst:
            return 'asc'
        elif sorted(lst, reverse=True) == lst:
            return 'desc'
    
    def is_bid_time(self):
        t = datetime.datetime.now()
        if t.hour==9 and t.minute>=15 and t.minute<=25:
            return True
        return False 
    
    def is_trading_time(self):
        t = datetime.datetime.now()
        if t.hour<9 or t.hour>15 or t.hour==12:
            return False
        if t.hour==9 and t.minute<30:
            return False
        if t.hour==11 and t.minute>30:
            return False
        return True

    def get_new_stock_info(self,page_num):
        url = "http://vip.stock.finance.sina.com.cn//corp/view/vRPD_NewStockIssue.php?page=%s"%(page_num)
        r = requests.get(url)
        bs = BeautifulSoup(r.content,'lxml')
        trs = bs.table.find_all('tr',class_='tr_2')
        ret = []
        for tr in trs:
            tds = tr.find_all('td')
            td_list = []
            for td in tds:
                td_text = td.text.lstrip().rstrip().replace('\n','')
                td_list.append(td_text)
            #print(','.join(td_list))
            ret.append(td_list)
        return ret[1:]  
    
    def get_stock_trading_dates(self,stock_id):
        in_mkt_date = self.db.get_in_mkt_date_from_id(stock_id)
        last_trading_date = self.db.get_last_trading_date()
        d1 = datetime.datetime.strptime(in_mkt_date,"%Y-%m-%d")
        d2 = datetime.datetime.strptime(last_trading_date,"%Y-%m-%d")
        return (d2-d1).days

    def get_yesterday(self): 
        today=datetime.date.today() 
        oneday=datetime.timedelta(days=1) 
        yesterday=today-oneday  
        return yesterday.strftime('%Y_%m_%d')

    def get_today(self):
        return datetime.date.today().strftime('%Y_%m_%d')
    
    def get_fp_stock_list(self):
        fp_file = "output/fp_%s.csv"%(self.get_yesterday())
        return self.get_stock_list_from_file(fp_file)
    
    def get_valid_stocks(self):
        return self.get_stock_list_from_file(self.valid_stock_file)

    
    def get_weighted_score(self,stock_id):
        score_list = self.db.get_stock_score_list(stock_id)
        ret = 0
        count = 1
        for score in score_list:
            ret = ret+score*count
            count = count/2
        return ret
    
    def get_stock_list_from_file(self,file_name):
        '''
        从csv文件中获取列表，返回一个数组
        '''
        if not os.path.exists(file_name):
            self.logger.info("File %s does not exist, please check...[get_stock_list_from_file]"%(file_name))
            return []
        with open(file_name,'r') as f:
            output = f.read()
        return output.split(',')    


    
    def save_stock_list_to_file(self,stock_list,file_name):
        #file_name = "./output/fp_%s.csv"%(self.last_trading_date.replace('-','_'))
        s_list_str = ','.join(stock_list)
        with open(file_name,'w') as f:
            f.write(s_list_str)    
    
    

    def get_summary_status(self,stock_list):
        ret = []
        title = " 股票名称（股票ID）| 开盘涨幅  | 当前涨幅  | 当前价格 |    成交量      |   成交金额   |     流通股   |     得分"
        ret.append(title)
        #print(stock_list)
        for s in stock_list:
            try:
                status = self.get_live_mon_items(s)            
                ret.append(status)
            except:
                self.logger.info("Exception on stock:%s"%(s))
        return ret

    def get_live_status(self,stock_id):
        ret = ""
        url = "http://hq.sinajs.cn/list=%s"%(stock_id)
        #self.logger.info(url)
        r = requests.get(url)
        if r.status_code != 200:
            return ret
        re_info = re.compile(r'="(.*)"')
        ret = re_info.findall(r.text)[0]
        return ret
       

    def get_live_mon_items(self,stock_id):
        info = self.get_live_status(stock_id).split(',')
        cur_price = float(info[3])
        last_day_price = float(info[2])
        open_price = float(info[1])
        stock_name = info[0]  
        #print(len(stock_name))  
        #print(2*'aaa')
        if len(stock_name)<4:
            #stock_name = "%s%s"%(''*(4-len(stock_name)),stock_name)
            stock_name = "%s%s"%('  ',stock_name)
        #print(len(stock_name))
        aoi = round((cur_price-last_day_price)*100/last_day_price,2)
        aoi_open = round((open_price-last_day_price)*100/last_day_price,2)
        volume = round(float(info[8])/1000000,2)
        rmb = round(float(info[9])/100000000,2)        
        db = StockDb()        
        float_shares = round(db.get_float_shares_from_id(stock_id)/100000000,2)
        score = round(self.get_weighted_score(stock_id),2)
        ret = "%s(%s) | %8s%% | %8s%% | %8s | %8s(万手) | %8s(亿) | %8s(亿) | %8s"\
        %(stock_name,stock_id,aoi_open,aoi,info[3],volume,rmb,float_shares,score) 
        return ret
    
    def get_live_mon_items_bid(self,stock_id):
        info = self.get_live_status(stock_id).split(',')
        self.logger.info(info)
        cur_price = float(info[11])
        last_day_price = float(info[2])
        #open_price = float(info[1])
        aoi = round((cur_price-last_day_price)*100/last_day_price,2)
        #aoi_open = (open_price-last_day_price)*100/last_day_price
        ret = "%s(%s) | %s | %s | %s"%(info[0],stock_id,aoi,round(cur_price,2),round(float(info[10])/10000,0))
        return ret       

    
    
    def get_live_price(self,stock_id):
        info = self.get_live_status(stock_id).split(',')
        return info[3]  
    
    def get_live_aoi_bid(self,stock_id):
        info = self.get_live_status(stock_id).split(',')
        cur_price = float(info[11])
        last_day_price = float(info[2])
        return round((cur_price-last_day_price)*100/last_day_price,2) 
    
    def get_live_aoi(self,stock_id):
        info = self.get_live_status(stock_id).split(',')
        cur_price = float(info[3])
        last_day_price = float(info[2])
        return round((cur_price-last_day_price)*100/last_day_price,2)  
    
    def get_delta(self,stock_id,day_num):        
        if day_num<=0 or day_num>10:
            self.logger.info("Please specify a daynum which between 1~10...")
            return 0 
        sql_cmd = "select sum(pchg) from (select * from tb_daily_info where stock_id='%s' order by date desc limit %s)"%(stock_id,day_num)        
        return float(self.db.query_db(sql_cmd)[0][0])
    
    def get_lift_in_one_day(self,stock_id,day_num):
        pass

    def get_increase_amount(self,stock_id,day_num):
        pass

    def get_volume_sum(self,stock_id,day_num):
        ret = 0
        for d in range(day_num):
            ret = ret + self.get_volume(stock_id,d)
        return round(ret,2)
    
    def get_volume(self,stock_id,day_num):
        pass
    
if __name__ == '__main__':
    t = StockUtil()    
    #print(t.get_market_status(0,100))
    stock_list = ['sz002472', 'sh600695', 'sh600462', 'sz002026', 'sz002856', 'sz000609', 'sz300659', 'sz002058', 'sh603106', 'sh603569', 'sh600846', 'sz002798', 'sz000971', 'sh600630', 'sz300234', 'sz300543', 'sz002328', 'sz002164', 'sz002226', 'sz300606', 'sz300636', 'sz002837', 'sh603165', 'sh600624', 'sz002417', 'sh603305', 'sh600283', 'sh600784', 'sz002680', 'sz300541', 'sz300651', 'sh603738', 'sz300607', 'sh603648', 'sh600366', 'sh600165', 'sh600355', 'sh603180', 'sz002288', 'sz002709', 'sh600278', 'sh600621', 'sz002492']
    print(t.get_summary_status(stock_list))
    #for s in stock_list:
    #    print(t.get_live_mon_items(s))
    #print(t.get_weighted_score('sz300751','2018-11-01'))
    #print(t.get_delta('sz000622',3))
    #print(t.get_last_trading_date())
    #print(t.get_volume('sz000002',0))
    #print(t.get_volume_sum('sh600290',3))
    #print(len(t.get_market_status(0,200)))
    #print(t.get_market_status(1,100)[99]['changepercent'])
    #print(t.get_market_status(0,100)[99]['changepercent'])
    #t.get_market_limit_up_number()
    #t.get_market_limit_down_number()
    #print(t.get_stock_name_from_id('sz000002'))
    #print(t.get_suspend_stocks())
    #print(t.get_live_price('sz000673'))
    #print(t.get_increase_amount('sz000002',0))
