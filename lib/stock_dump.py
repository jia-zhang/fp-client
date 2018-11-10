# -*- coding: utf-8 -*-  
import requests
import re
import time
import os
import json
import random
import datetime
import subprocess
import sys
from logger import Logger
from stock_util import StockUtil

class StockDump():
    def __init__(self):
        #self.stock_list_url = "http://quote.eastmoney.com/stocklist.html"
        self.logger = Logger("StockDump")
        #with open('last_dump_date.txt','r') as f:
        #    self.last_dump_date = f.read()
        self.stock_list_file = 'stocks.csv'
        self.default_count = 15
        self.util = StockUtil()
        self.last_trading_date = self.util.get_last_trading_date()
        if 'linux' in sys.platform:
            self.zip_cmd = '7za'
        else:
            self.zip_cmd = "util\\7z"

    def download_valid_stock_list(self):        
        local_file = "valid_stock.csv"
        download_url = "https://s3.eu-central-1.amazonaws.com/g1-build/tmp/%s"%(local_file)
        r = requests.get(download_url) 
        with open(local_file, "wb") as f:
            f.write(r.content)
    
    def get_stock_list(self):
        '''
        应该只需要调用一次，以后统一用valid_stock.csv
        '''
        resp = requests.get("http://quote.eastmoney.com/stocklist.html")
        resp.encoding = 'gb2312'
        s = r'<li><a target="_blank" href="http://quote.eastmoney.com/(.*?).html">'
        pat = re.compile(s)
        codes = pat.findall(resp.text)
        return codes

    def save_stock_list(self,file_name):
        '''
        同上
        '''
        ret = []
        all_stocks = self.get_stock_list()
        for n in all_stocks:
            if n.startswith('sz00') or n.startswith('sh60') or n.startswith('sz300'):
                ret.append(n)
        with open(file_name,'w') as f:
            f.write(",".join(ret))
       
    def get_stock_detail(self,stock_id,time_range,count,retry_num=3):
        '''
        获取某股票在time_range内的动态数据，开盘价，收盘价之类。
        统一从新浪拿，每天15：00以后拿一次就可以。
        '''
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        ret = ''
        detail_url = ("http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?"
                    "symbol=%s&scale=%s&ma=no&datalen=%s"
        )%(stock_id,time_range,count)
        #self.logger.info(detail_url)
        try:
            resp = requests.get(detail_url,timeout=60)
            if resp.status_code!=200:
                requests.raise_for_status()
            ret = resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"')\
            .replace('high','"high"').replace('close','"close"').replace('volume','"volume"')
        except requests.exceptions.ConnectionError as e:
            self.logger.info("Connection error...exit")
            return ret
        except:
            #html=None
            if retry_num>0:
            #如果不是200就重试，每次递减重试次数
                self.logger.info("Non 200 respose, retry. Status_code=%s"%(resp.status_code))
                return self.get_stock_detail(url,stock_id,time_range,count,retry_num-1)
        return ret   
    
    def dump_stock_dynamic_daily(self):
        self.dump_stock_dynamic(240,self.default_count)
    
    def dump_stock_dynamic_weekly(self):
        self.dump_stock_dynamic(1680,self.default_count)
    
    def dump_stock_dynamic_monthly(self):
        self.dump_stock_dynamic(7200,self.default_count)
    
    def dump_stock_dynamic(self,time_range,count,force=1):
        '''
        Dump stock info from sina.
        time_range = 240, 1680, 7200 - daily, weekly, monthly
        count = number of data need to  be dumpped        
        '''  
        self.logger.info(self.util.get_last_trading_date())
        s_list = self.util.get_valid_stocks()
        if time_range == 240:
            dump_type = 'daily'
        elif time_range == 1680:
            dump_type = 'weekly'
        elif time_range == 7200:
            dump_type = 'monthly'
        for s in s_list:
            self.logger.info("Dumping stock %s dynamic %s..."%(s,dump_type))
            #file_name = self.util.get_dynamic_file_from_id(s)
            file_name = self.util.get_dynamic_file_from_id(s,dump_type)
            #self.logger.info(file_name)
            if (force==0 and os.path.exists(file_name)):
                self.logger.info("%s already exists, skip"%(s))
                continue
            stock_detail = self.get_stock_detail(s,time_range,count)
            with open(file_name,'w') as f:
                f.write(stock_detail)
            
    def dump_stock_static(self,force=0):
        '''
        Get some very basic static information from xueqiu.com
        if force==1, will overwrite exists json file, please be careful
        '''
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        re_fload_shares = re.compile(r'"float_shares":(\d*?),')
        re_stock_name = re.compile(r'"name":(.*?),')
        re_market_capital = re.compile(r'"market_capital":(.*?),')
        s_list = self.util.get_valid_stocks()
        for s in s_list:
            self.logger.info("Dumping stock static %s..."%(s))
            file_name = self.util.get_static_file_from_id(s)
            if (force==0 and os.path.exists(file_name)):
                self.logger.info("%s already exists, skip"%(s))
                continue
            try:
                master_dict = {}
                resp = requests.get("https://xueqiu.com/S/%s"%(s),headers=headers)
                if (resp.status_code==404):
                    self.logger.info("Get code 404 on stock %s"%(s))                    
                    continue
                elif(resp.status_code!=200):
                    self.logger.info("Get code %s on stock %s"%(resp.status_code,s))
                    continue
                resp.encoding = 'utf-8'            
                stock_dict = {}
                stock_dict['float_shares'] = str(re_fload_shares.findall(resp.text)[0])  
                stock_dict['stock_name'] = str(re_stock_name.findall(resp.text)[0])
                stock_dict['market_capital'] = str(re_market_capital.findall(resp.text)[0])
                master_dict[s] = stock_dict
                with open(file_name,'w') as f:
                    f.write(json.dumps(master_dict))
            except:
                self.logger.info("exception on stock %s!"%(s))
    
    def zip_dynamic(self,folder):
        #cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        cur_date = self.last_trading_date.replace("-","_")
        zip_cmd = "%s a dynamic_%s.zip %s"%(self.zip_cmd,cur_date,folder)
        return subprocess.call(zip_cmd,shell=True) 
    
    def upload_dynamic(self,s3_bucket):
        #cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        cur_date = self.last_trading_date.replace("-","_")
        upload_cmd = "aws s3 cp dynamic_%s.zip %s/dynamic_%s.zip --acl public-read"%(cur_date,s3_bucket,cur_date)
        return subprocess.call(upload_cmd,shell=True)
    
    def download_dynamic_from_s3(self,s3_bucket):
        #cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        cur_date = self.last_trading_date.replace("-","_")
        download_cmd = "aws s3 cp %s/dynamic_%s.zip ."%(s3_bucket,cur_date)
        return subprocess.call(download_cmd,shell=True)
    
    def download_dynamic_from_url(self):
        #cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        cur_date = self.last_trading_date.replace("-","_")
        local_file = "dynamic_%s.zip"%(cur_date)
        download_url = "https://s3.eu-central-1.amazonaws.com/g1-build/tmp/dynamic_%s.zip"%(cur_date)
        r = requests.get(download_url) 
        with open(local_file, "wb") as f:
            f.write(r.content)
    
    def download_static_from_url(self):
        local_file = "static.zip"
        download_url = "https://s3.eu-central-1.amazonaws.com/g1-build/tmp/%s"%(local_file)
        r = requests.get(download_url) 
        with open(local_file, "wb") as f:
            f.write(r.content)
    

    def unzip_dynamic(self,folder):
        #cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        cur_date = self.last_trading_date.replace("-","_")
        zip_cmd = "%s x dynamic_%s.zip -o%s -aoa"%(self.zip_cmd,cur_date,folder)
        return subprocess.call(zip_cmd,shell=True) 

    def unzip_static(self,folder):
        zip_cmd = "%s x static.zip -o%s -aoa"%(self.zip_cmd,folder)
        return subprocess.call(zip_cmd,shell=True) 
    
    def zip_and_upload(self,folder,s3_bucket):
        pass

if __name__ == '__main__':
    t = StockDump()
    t.logger.info("start")
    #t.dump_stock_dynamic(240,15)
    t.dump_stock_dynamic_daily()
    t.zip_dynamic('./data/dynamic')
    t.upload_dynamic('s3://g1-build/tmp')
    #t.download_dynamic('s3://g1-build/tmp')
    #t.unzip_dynamic('./data')
    #t.dump_stock_dynamic(240,15)
    #t.logger.info("end")


