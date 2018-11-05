import requests
import re
import time
import os
import json
from logger import Logger

class StockUtil():
    def __init__(self):
        self.logger = Logger("StockUtil")
        self.valid_stock_file = "valid_stock.csv"
        self.last_trading_day = self.get_last_trading_date()
        pass
    
    def get_valid_stocks(self):
        return self.get_stock_list_from_file(self.valid_stock_file)

    def get_trading_stocks(self):
        '''
        返回一个目前正常交易的列表
        '''
        s_list = self.get_valid_stocks()
        ret = []
        for s in s_list:
            file_name = self.get_dynamic_file_from_id(s)
            output = self.check_file_and_read(file_name)
            if output == '':
                continue
            stock_detail = eval(output)
            if self.last_trading_day == stock_detail[-1]['day']:
                ret.append(s)
                #self.logger.info(self.get_stock_name_from_id(s))
        return ret
    
    def get_suspend_stocks(self):
        '''
        返回一个停牌的列表
        '''
        s_list = self.get_valid_stocks()
        ret = []
        for s in s_list:
            file_name = self.get_dynamic_file_from_id(s)
            with open(file_name,'r') as f:
                output = f.read()
            if output == "null":
                ret.append(s)
                continue
            stock_detail = eval(output)
            if self.last_trading_day != stock_detail[-1]['day']:
                ret.append(s)
                self.logger.info(self.get_stock_name_from_id(s))
        return ret
    
    def check_file_and_read(self,file_name):
        if not os.path.exists(file_name):
            self.logger.info("File %s does not exist...Please check...[check_file_and_read]"%(file_name))
            return ''
        with open(file_name,'r') as f:
            output = f.read()
        if output == "null":
            self.logger.info("File %s is null, please check..."%(file_name))
            return ''
        return output
    
    def get_static_file_from_id(self,stock_id):
        return "./data/static/%s.static.json"%(stock_id)
    
    def get_dynamic_file_from_id(self,stock_id):
        return "./data/dynamic/%s.json.d"%(stock_id)
    
    def check_dynamic_data(self):
        ret = False
        if self.get_last_trading_date() == self.get_last_trading_date_from_file():
            ret = True
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
    
    def get_last_trading_date(self):
        '''
        获取最近一次的交易日。获取上证指数的最后交易数据即可。
        '''
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        resp = requests.get(detail_url)
        return eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']
    
    def get_last_trading_date_from_file(self,stock_id='sh000001'):
        file_name = self.get_dynamic_file_from_id(stock_id)
        output = self.check_file_and_read(file_name)
        stock_detail = eval(output)
        return stock_detail[-1]['day']

    def get_live_status(self,stock_id):
        ret = ""
        url = "http://hq.sinajs.cn/list=%s"%(stock_id)
        r = requests.get(url)
        if r.status_code != 200:
            return ret
        re_info = re.compile(r'="(.*)"')
        ret = re_info.findall(r.text)[0]
        return ret
    
    def get_live_price(self,stock_id):
        info = self.get_live_status(stock_id).split(',')
        return info[3]  
    
    def get_live_aoi(self,stock_id):
        info = self.get_live_status(stock_id).split(',')
        cur_price = float(info[3])
        last_day_price = float(info[2])
        return (cur_price-last_day_price)*100/last_day_price  
    
    def get_stock_name_from_id(self,stock_id):
        info = self.get_live_status(stock_id).split(',')
        return info[0] 
    
    def get_stock_name_from_id_old(self,stock_id):
        file_name = self.get_static_file_from_id(stock_id)
        if not os.path.exists(file_name):
            return ''
        f = open(file_name,'r')
        json_output = json.load(f)
        f.close()
        return json_output[stock_id]['stock_name']
    
    def get_delta(self,stock_id,day_num):
        '''
        获取day_num天前到目前收盘价的delta值，以%表示。
        day_num取值在1~10之间，太长或者等于0没有意义。
        day_num = 1（1天前的收盘价和最后一天收盘价的delta）
        day_num = 10（10天前的收盘价和最后一天收盘价的delta）
        '''
        if day_num<=0 or day_num>10:
            self.logger.info("Please specify a daynum which between 1~10...")
            return 0 
        file_name = self.get_dynamic_file_from_id(stock_id)
        output = self.check_file_and_read(file_name)
        if output=='':
            return 0
        stock_detail = eval(output)
        if abs(-1-day_num)>len(stock_detail):
            #print("%s:No data on day %s"%(stock_id,day_num))
            return 0
        if self.last_trading_day != stock_detail[-1]['day']:
            #print("停牌或者怎样了%s"%(stock_id))
            return 0
        price_start = float(stock_detail[-1-day_num]['close'])
        #print(price_start)        
        price_end = float(stock_detail[-1]['close'])
        #print(price_end)
        lift_status = (price_end-price_start)*100/price_start
        return lift_status
    
    def get_lift_in_one_day(self,stock_id,day_num):
        '''
        获取前day_num天的高点到收盘价的差值，用来回避大阴线。
        day_num取值在0~9之间。
        '''
        if day_num<0 or day_num>9:
            self.logger.info("Please specify a daynum which between 0~9...")
            return 0 
        file_name = self.get_dynamic_file_from_id(stock_id)
        output = self.check_file_and_read(file_name)
        if output=='':
            return 0
        stock_detail = eval(output)
        if abs(-1-day_num)>len(stock_detail):
            self.logger.info("%s:No data on day %s"%(stock_id,day_num))
            return 0     
        if self.last_trading_day != stock_detail[-1]['day']:
            self.logger.info("Stock %s's last trading day not equals to sh000001's last trading day, please check..."%(stock_id))
            return 0   
        price_high = float(stock_detail[-1-day_num]['high'])
        #print(price_start)        
        price_end = float(stock_detail[-1-day_num]['close'])
        #print(price_end)
        lift_status = (price_end-price_high)*100/price_high
        return lift_status


    def get_increase_amount(self,stock_id,day_num):
        '''
        获取某股票前day_num的当天涨跌幅。需要保证动态数据json文件里面有值，否则会报错(to be fixed)
        day_num取值范围在0~9之间。
        比如，获取前一天的get_increase_amount('sz000002',1)
        获取最后一天的get_increase_amount('sz000002',0)
        '''
        if day_num<0 or day_num>9:
            self.logger.info("Please specify a daynum which between 0~9...")
            return 0 
        file_name = self.get_dynamic_file_from_id(stock_id)
        output = self.check_file_and_read(file_name)
        if output=='':
            return 0
        stock_detail = eval(output)
        if abs(-2-day_num)>len(stock_detail):
            self.logger.info("%s:No data on day %s"%(stock_id,day_num))
            return 0     
        if self.last_trading_day != stock_detail[-1]['day']:
            self.logger.info("Stock %s's last trading day not equals to sh000001's last trading day, please check..."%(stock_id))
            return 0   
        price_start = float(stock_detail[-2-day_num]['close'])
        #print(price_start)        
        price_end = float(stock_detail[-1-day_num]['close'])
        #print(price_end)
        lift_status = (price_end-price_start)*100/price_start
        return lift_status
    
    def get_volume(self,stock_id,day_num):
        '''
        获取某股票前day_num的当天换手率。day_num=0代表最后一天，day_num=1代表最后前一天
        '''
        file_name = self.get_dynamic_file_from_id(stock_id)
        output = self.check_file_and_read(file_name)
        if output == '':
            return 0
        stock_detail = eval(output)
        if abs(-1-day_num)>len(stock_detail):
            self.logger.info("%s:No data on day %s"%(stock_id,day_num))
            return 0
        volume = int(stock_detail[-1-day_num]['volume'])

        file_name = self.get_static_file_from_id(stock_id)
        if not os.path.exists(file_name):
            return 0
        f = open(file_name,'r')
        json_output = json.load(f)
        f.close()
        gb = json_output[stock_id]['float_shares']
        if(gb==0):
            self.logger.info("stock_id: %s,float_share is zero"%(stock_id))
        try:
            ret = volume*100/float(gb)
        except:
            self.logger.info("stock_id: %s,float_share is zero"%(stock_id))
        return ret
    
    def add_property(self,stock_id,property_dict):
        '''
        为某股票添加一个新的字段，会改写股票的static文件。
        #t.add_propery('sh600000',{"tag1":{"ddd":"ccc"}})    
        '''
        file_name = self.get_static_file_from_id(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        for key in property_dict.keys():
            info[stock_id][key] = property_dict[key]
        self.logger.info(info)
        with open(file_name,'w') as f:
            f.write(json.dumps(info))
    
    def remove_property(self,stock_id,property_key):
        '''
        删除某股票的某个字段，会改写股票的static文件。
        #t.remove_property('sh600000','tag1')
        '''
        file_name = self.get_static_file_from_id(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        info[stock_id].pop(property_key)
        self.logger.info(info)
        with open(file_name,'w') as f:
            f.write(json.dumps(info))

if __name__ == '__main__':
    t = StockUtil()
    print(t.check_dynamic_data())
    #print(t.get_stock_name_from_id('sz000002'))
    #print(t.get_suspend_stocks())
    #print(t.get_live_price('sz000673'))
    #print(t.get_increase_amount('sz000002',0))
