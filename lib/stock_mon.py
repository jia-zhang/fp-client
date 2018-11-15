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
        pass

    def get_xueqiu_info(self,url):
        cookie_url = "https://xueqiu.com"
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        r = requests.get(cookie_url,headers=headers)
        cookies = r.cookies
        r1 = requests.get(url,headers=headers,cookies=cookies)
        #self.logger.info(r1.text)
        stock_list = eval(r1.text)['stocks']
        return DataFrame(stock_list)


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
        df1 = df[['symbo','name','changepercent','trade','open','high','low','volume','turnoverratio','mktcap']]
        print(df1)
        status = self.get_market_status(1,1,n)
        df = DataFrame(status)
        df1 = df[['symbo','name','changepercent','trade','open','high','low','volume','turnoverratio','mktcap']]
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

    def sum(self,stock_list):
        db = StockDb()    
        self.logger.info("StockID | StockName | 3日涨幅 | 5日涨幅 | 7日涨幅 | 3日换手 | 5日换手 | 7日换手")  
        for s in stock_list:    
            try: 
                stock_name = db.get_stock_name_from_id(s)   
                pchg_3 = round(db.get_sum_n_pchg(s,3),2)
                pchg_5 = round(db.get_sum_n_pchg(s,5),2)
                pchg_7 = round(db.get_sum_n_pchg(s,7),2)
                to_3 = round(db.get_sum_n_turnover(s,3),2)
                to_5 = round(db.get_sum_n_turnover(s,5),2)
                to_7 = round(db.get_sum_n_turnover(s,7),2)
                self.logger.info("%s | %s | %s | %s | %s | %s | %s | %s"%(s,stock_name,pchg_3,pchg_5,pchg_7,to_3,to_5,to_7))
            except:
                self.logger.info("Exception on stock %s"%(s))

    


    def check_fp_list(self):
        db = StockDb()
        fp_types = ['龙头','潜力','屌丝潜力']        
        date = db.get_last_trading_date()
        for t in fp_types:
            s_list = db.get_fp_result(date,t).split(',')
            self.check_stock_list(s_list)     

    def get_bid_sample_list(self,top_n=50): #run on 9:20, get stock_list which is in top n
        url = 'https://xueqiu.com/stock/cata/stocklist.json?page=1&size=%s&order=desc&orderby=percent&type=11%%2C12&_=1541985912951'%(top_n)
        df = self.get_xueqiu_info(url)
        df1 =  df[['code','name','current','percent','volume']]  
        print(df1)  
        s_list = df1['code'].values.tolist()
        #print(s_list)
        return s_list
    
    def mon_bid(self):
        sample_list = self.get_bid_sample_list()
        while True:
            time.sleep(5) #every 20 seconds, check diff(new_list,sample_list)...
            new_list = self.get_bid_sample_list()
            check_list = []
            for s in new_list:
                if s not in sample_list:
                    check_list.append(s)
            for s in check_list:
                if s.startswith('60'):
                    stock_id = "sh%s"%(s)
                else:
                    stock_id = "sz%s"%(s)    
                self.logger.info("================Monitor==============")
                self.logger.info("股票名称（股票ID）| 涨幅 | 竞买价 | 竞买量（万手）") 
                status = self.util.get_live_mon_items_bid(stock_id)
                self.logger.info(status)

if __name__ == '__main__':
    t = StockMon()
    #stock_list = t.get_top_n_list(100)
    #print(stock_list)
    t.sum_top_n_list(0,100)
    #t.get_top_and_bottom(50)
    #df = DataFrame(t.get_market_status(0,1,50))
    #print(df)
    #t.get_bid_sample_list()
    #t.mon_bid()

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
    