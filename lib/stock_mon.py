from stock_util import StockUtil
from logger import Logger
from stock_db import StockDb
import time
import threading
import requests
from pandas import DataFrame
import pandas as pd

class StockMon():
    def __init__(self):
        self.logger = Logger("StockMon")
        self.util = StockUtil()

    def get_xueqiu_info(self,url):
        cookie_url = "https://xueqiu.com"
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        r = requests.get(cookie_url,headers=headers)
        cookies = r.cookies
        r1 = requests.get(url,headers=headers,cookies=cookies)
        #self.logger.info(r1.text)
        stock_list = eval(r1.text)['stocks']
        return DataFrame(stock_list)
    
    def get_market_status_from_xueqiu(self,direction,page_number,page_size):
        #direction = asc 跌幅榜， direction = desc 涨幅榜
        url = "https://xueqiu.com/stock/cata/stocklist.json?page=%s&size=%s&order=%s&orderby=percent&type=11%%2C12&_=1541985912951"%(page_number,page_size,direction)
        #self.logger.info(url)
        return self.get_xueqiu_info(url)

    def get_market_status(self,direction,page_number,page_size,use_proxy=0):
        #direction=0 means top n, direction=1 means bottom n
        proxies = {'http': 'http://18.197.117.119:8080', 'https': 'http://18.197.117.119:8080'}
        detail_url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?\
        page=%s&num=%s&sort=changepercent&asc=%s&node=hs_a&symbol=&_s_r_a=init"%(page_number,page_size,direction)
        if use_proxy==1:
            resp = requests.get(detail_url,proxies=proxies)
        else:
            resp = requests.get(detail_url)
        #self.logger.info(resp.text)
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
    
    def get_zt_number(self):
        #Get zt number
        market_status = self.get_market_status(0,1,100)
        for i in range(100):
            if float(market_status[i]['changepercent'])<9.7:
                self.logger.info("涨停个数：%s"%i)
                return i       

    def get_dt_number(self):
        #Get dt number
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
        status = self.util.get_summary_status(stock_list)
        self.logger.info(status)        


    def monitor_after_bid(self,stock_list,refresh_interval):
        while True:        
            self.logger.info("===============Monitor===============")
            self.logger.info("股票名称（股票ID）| 开盘涨幅 | 当前涨幅 | 当前价格 | 成交量（万手）| 成交金额（亿）")
            for s in stock_list:
                self.logger.info(self.util.get_live_mon_items(s))
            time.sleep(refresh_interval)  

    def check_top_and_bottom(self,n):
        status = self.get_market_status(0,1,n)
        df = DataFrame(status)
        df1 = df[['symbo','name','changepercent','trade','open','high','low','volume','turnoverratio']]
        print(df1)
        status = self.get_market_status(1,1,n)
        df = DataFrame(status)
        df1 = df[['symbo','name','changepercent','trade','open','high','low','volume','turnoverratio']]
        print(df1)
    
    def get_top_n_df(self,direction,n):
        #direction=0 means top n, direction=1 means bottom n
        status = self.get_market_status(direction,1,n)
        df = DataFrame(status)
        ret = df[['symbo','name','changepercent','trade','open','turnoverratio']]
        print(ret)
        return ret
    
    def sum_top_n_list(self,direction,n):
        '''
        tmp_csv = 'tmp.csv'
        df = self.get_top_n_df(direction,n)
        df.to_csv(tmp_csv,index=False)
        f = open(tmp_csv,'r')
        out = open('out.csv','w')
        line_number = 0
        sample_count = 3
        for line in f.readlines():
            item = line.replace('\n','')
            if line_number==0:
                target_line = ",%s,"%(item)                
            else:
                s = item.split(',')[0]
                s_name = item.split(',')[1]
                #self.logger.info(s)
                if s_name.startswith('N'):
                    target_line = "%s,%s,"%(line_number,item)
                else:
                    db = StockDb()  
                    tmp = []
                    turn_over_list = db.get_last_n_turnover(s,sample_count)
                    for t in turn_over_list:
                        tmp.append(str(t))
                    turn_over_sample = ','.join(tmp)
                    pchg_list = db.get_last_n_pchg(s,sample_count)
                    for t in pchg_list:
                        tmp.append(str(t))
                    pchg_sample = ','.join(tmp)
                    target_line = ("%s,%s,%s,%s"%(line_number,item,turn_over_sample,pchg_sample))
            line_number = line_number+1
            out.write("%s\n"%(target_line))
        f.close()
        out.close()
        '''
        df1 = pd.read_csv('out.csv',index_col=0)
        with open('output.html','w',encoding="gb2312") as f:
            f.write(df1.to_html())  

    def get_bid_sample_list(self,top_n=100): #run on 9:20, get stock_list which is in top n
        url = 'https://xueqiu.com/stock/cata/stocklist.json?page=1&size=%s&order=desc&orderby=percent&type=11%%2C12&_=1541985912951'%(top_n)
        df = self.get_xueqiu_info(url)
        df1 =  df[['symbol','name','current','percent','volume']]  
        #print(df1)  
        s_list = df1['symbol'].values.tolist()
        #print(s_list)
        return s_list
    
    def mon_bid(self):
        sample_list = self.get_bid_sample_list()
        f = open('bid.txt','w')
        while True:
            time.sleep(20) #every 20 seconds, check diff(new_list,sample_list)...
            new_list = self.get_bid_sample_list()
            check_list = []
            for s in new_list:
                if s not in sample_list:
                    check_list.append(s)
            for s in check_list:                  
                self.logger.info("================Please check the following==============")                
                status = self.util.get_live_status(s)
                self.logger.info(s)
                self.logger.info(status)
                f.write(s)
        f.close()

if __name__ == '__main__':
    t = StockMon()
    t.mon_bid()
    #df = t.get_bid_sample_list()
    
    #stock_list = t.get_top_n_list(100)
    #print(stock_list)
    #t.sum_top_n_list(0,100)
    #check(50)
    #df = DataFrame(t.get_market_status(0,1,50))
    #df1 = df.iloc[:,10:20]
    #df1 = df.iloc[:,0:10]
    #print(df1)
    #t.get_bid_sample_list()
    #t.mon_bid()

    '''   
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
    