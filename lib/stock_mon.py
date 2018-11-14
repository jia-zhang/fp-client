from stock_util import StockUtil
from logger import Logger
from stock_db import StockDb
import time
import threading
import requests
from pandas import DataFrame

class StockMon():
    def __init__(self):
        self.logger = Logger("StockMon")
        self.util = StockUtil()
        pass

    def get_xueqiu_info(self,url):
        cookie_url = "https://xueqiu.com"
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        r = requests.get(cookie_url,headers=headers)
        cookies = r.cookies
        r1 = requests.get(url,headers=headers,cookies=cookies)
        #self.logger.info(r1.text)
        stock_list = eval(r1.text)['stocks']
        return stock_list


    def get_market_status(self,direction,page_number,page_size):
        proxies = {'http': 'http://18.197.117.119:8080', 'https': 'http://18.197.117.119:8080'}
        detail_url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?\
        page=%s&num=%s&sort=changepercent&asc=%s&node=hs_a&symbol=&_s_r_a=init"%(page_number,page_size,direction)
        #resp = requests.get(detail_url,proxies=proxies)
        resp = requests.get(detail_url)
        #print(resp.text)
        if resp.text=='null':
            return ''
        elif '?xml' in resp.text:
            self.logger.info(resp.text)
        else:            
            return eval(resp.text.replace('symbol','"symbo"').replace('code','"code"').replace('name','"name"').replace('trade','"trade"').\
        replace('pricechange','"pricechange"').replace('changepercent','"changepercent"').replace('buy','"buy"').replace('sell','"sell"').\
        replace('settlement','"settlement"').replace('open','"open"').replace('high','"high"').replace('low','"low"').\
        replace('volume','"volume"').replace('amount','"amount"').replace('ticktime','"ticktime"').replace('per:','"per":').\
        replace('pb','"pb"').replace('mktcap','"mktcap"').replace('nmc','"nmc"').replace('turnoverratio','"turnoverratio"'))
    
    def get_market_limit_up_number(self):
        '''
        获取市场涨停个数
        '''
        ret = 0
        market_status = self.get_market_status(0,1,100)
        for i in range(100):
            if float(market_status[i]['changepercent'])<9.7:
                self.logger.info("涨停个数：%s"%i)
                return i       

    def get_market_limit_down_number(self):
        '''
        获取市场跌停个数
        '''
        ret = 0
        market_status = self.get_market_status(1,1,100)
        for i in range(100):
            if float(market_status[i]['changepercent'])>-9.7:
                self.logger.info("跌停个数：%s"%i)
                return i       
    
    def monitor_bid(self,stock_list,refresh_interval):
        sample = {}
        for s in stock_list:
            aoi = self.util.get_live_aoi_bid(s)
            sample[s] = aoi
        while True:
            self.logger.info("================Monitor==============")
            self.logger.info("股票名称（股票ID）| 涨幅 | 竞买价 | 竞买量（万手）")            
            for s in stock_list:
                status = self.util.get_live_mon_items_bid(s)
                aoi = self.util.get_live_aoi_bid(s)   
                if aoi-sample[s]>1:
                    plus_icon = "[↑+%s]"%(round(aoi-sample[s],2))
                    self.logger.info("*%s %s"%(status,plus_icon))
                elif aoi-sample[s]<-1:
                    plus_icon = "[↓%s]"%(round(aoi-sample[s],2))
                    self.logger.info("*%s %s"%(status,plus_icon))
                else:
                    self.logger.info(status) 
                '''               
                if aoi-sample[s]>2:
                    self.logger.info("Stock %s aoi increased from %s to %s"%(s,sample[s],aoi))
                elif aoi-sample[s]<-2:
                    self.logger.info("Stock %s aoi dropped from %s to %s"%(s,sample[s],aoi))
                '''
                sample[s] = aoi
            time.sleep(refresh_interval)

    def check_stock_list(self,stock_list):      
        self.logger.info("================Monitor==============")
        self.logger.info("  股票名称（股票ID）       | 开盘涨幅  | 当前涨幅  | 当前价格 |    成交量      |   成交金额   | 昨日换手 | 昨日涨幅  |    流通股")            
        for s in stock_list:
            status = self.util.get_live_mon_items(s)  
            self.logger.info(status)        


    def monitor_after_bid(self,stock_list,refresh_interval):
        while True:        
            self.logger.info("===============Monitor===============")
            self.logger.info("股票名称（股票ID）| 开盘涨幅 | 当前涨幅 | 当前价格 | 成交量（万手）| 成交金额（亿）")
            for s in stock_list:
                self.logger.info(self.util.get_live_mon_items(s))
            time.sleep(refresh_interval)  

    def get_top_and_bottom(self,n):
        status = self.get_market_status(0,1,n)
        df = DataFrame(status)
        df1 = df[['code','name','changepercent','trade','open','high','low','volume','turnoverratio','mktcap']]
        print(df1)
        status = self.get_market_status(1,1,n)
        df = DataFrame(status)
        df1 = df[['code','name','changepercent','trade','open','high','low','volume','turnoverratio','mktcap']]
        print(df1)


    def check_fp_list(self):
        db = StockDb()
        fp_types = ['龙头','潜力','屌丝潜力']        
        date = db.get_last_trading_date()
        for t in fp_types:
            s_list = db.get_fp_result(date,t).split(',')
            self.check_stock_list(s_list)        

if __name__ == '__main__':
    t = StockMon()
    #t.get_top_and_bottom(50)
    t.check_fp_list()
    '''
    url = 'https://xueqiu.com/stock/cata/stocklist.json?page=1&size=100&order=desc&orderby=percent&type=11%2C12&_=1541985912951'
    url2 = 'https://xueqiu.com/stock/cata/stocklist.json?page=1&size=30&order=desc&orderby=percent&type=11%2C12&_=1541985912951'
    for i in range(1,2):
        url = "https://xueqiu.com/stock/cata/stocklist.json?page=%s&size=100&order=desc&orderby=percent&type=11%%2C12&_=1541985912951"%(i)
        print(DataFrame(t.get_xueqiu_info(url)))
        url2 = "https://xueqiu.com/stock/cata/stocklist.json?page=%s&size=100&order=asc&orderby=percent&type=11%%2C12&_=1541985912951"%(i)
        print(DataFrame(t.get_xueqiu_info(url2)))
    
    f = open('t1.csv','w')
    for i in range(1,40):
        status = t.get_market_status(0,i,100)
        if status == '':
            print('No data in this %s page!'%i)
            break
        else:            
            df = DataFrame(status)
            csv_file = 't.csv'
            #df1 = df.loc[df.turnoverratio>5]
            #df1 = df.iloc[:,10:20]
            df1 = df[['code','open','high','low','trade','volume','turnoverratio','changepercent']]    
            print(df1)
            df1.to_csv(f,header=False,index=False)
    f.close()

    '''
    