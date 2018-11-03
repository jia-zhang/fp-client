import requests
import re
import time
import os
import json
import pdb
from lib.stock_util import StockUtil
from lib.logger import Logger

class StockFilter():
    def __init__(self):
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        #detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        #resp = requests.get(detail_url)
        self.logger = Logger("StockFilter")
        self.util = StockUtil()
        #self.last_trading_day = eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        #replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']

    def check_if_time_available(self):
        pass
    
    
    def get_volume_within_days(self,stock_list,day_num,volume_critiria):  
        '''
        过滤stock_list，返回day_num天前到现在，换手率超过volume_critiria的股票
        例如，get_volume_within_days(stock_list, 3, 20)表示返回3天内总换手超过20%的股票
        '''      
        ret = []
        for s in stock_list:
            volume = 0
            for i in range(day_num):
                volume = volume+self.util.get_volume(s,i)
            if volume>=volume_critiria:
                #self.logger.info("%s:%s"%(self.util.get_stock_name_from_id(s),volume))
                ret.append(s)
        self.logger.info("Found %s stocks after get volume sum within %s days"%(len(ret),day_num))
        return ret
    
    def get_delta_within_days(self,stock_list,day_num,delta_criteria):
        '''
        过滤stock_list，返回delta_day内涨幅>delta_critira的股票列表
        例如，get_delta_within_days(stock_list,3,20)表示拿到3天内涨幅>20%的股票列表
        '''
        self.logger.info("Start, get delta>%s stocks..."%(delta_criteria))
        ret=[]
        for s in stock_list:
            delta = self.util.get_delta(s,day_num)
            #self.logger.info("%s:%s"%(s,delta))
            if(delta>delta_criteria and s not in ret):
                ret.append(s)
        self.logger.info("End, found %s stocks"%(len(ret)))
        self.logger.info("============================\n\n")
        return ret
    
    def get_big_increase_within_days(self,stock_list,day_num,increase_criteria):
        '''
        过滤stock_list,如果在day_num内，出现大阳线，一般是涨停（上涨超过drop_critiria），则返回这些股票的list。
        返回一个stock列表，拿到所有n日内有大阳线的股票。
        '''
        self.logger.info("Filter big increase within %s days"%(day_num))
        ret = []
        for s in stock_list:
            for day in range(day_num):
                increase = self.util.get_increase_amount(s,day)
                if increase>=increase_criteria:
                    #self.logger.info("Get stock %s big increase>criteria...Increase day: %s"%(s,day))
                    ret.append(s)
                    break
        self.logger.info("Found %s stocks which have big increase within %s days"%(len(ret),day_num))
        return ret
    
    def filter_big_lift_within_days(self,stock_list,day_num,lift_criteria):
        '''
        过滤stock_list,如果在day_num内，出现大阴线形态2（高点和收盘差超过lift_critiria），则剔除这些股票。
        返回一个stock列表，去掉了所有n日内有大阴线形态2的股票。
        '''
        tmp = []
        self.logger.info("Filter big lift within %s days"%(day_num))
        #print(stock_list)
        for s in stock_list:
            #self.logger.info(s)
            for day in range(day_num):
                lift = self.util.get_lift_in_one_day(s,day)
                #self.logger.info("%s:%s"%(s,drop))
                if lift<lift_criteria:
                    #pdb.set_trace()
                    self.logger.info("Remove stock %s big lift>criteria...Lift day: %s"%(s,day))
                    tmp.append(s)
                    break
        ret = list(set(stock_list) ^ set(tmp))
        self.logger.info("Found %s stocks after filtering big lift within %s days"%(len(ret),day_num))
        return ret
    
    def filter_big_drop_within_days(self,stock_list,day_num,drop_criteria):
        '''
        过滤stock_list,如果在day_num内，出现大阴线（下跌超过drop_critiria），则剔除这些股票。
        返回一个stock列表，去掉了所有n日内有大阴线的股票。
        '''
        tmp = []
        self.logger.info("Filter big drop within %s days"%(day_num))
        #print(stock_list)
        for s in stock_list:
            #self.logger.info(s)
            for day in range(day_num):
                drop = self.util.get_increase_amount(s,day)
                #self.logger.info("%s:%s"%(s,drop))
                if drop<drop_criteria:
                    #pdb.set_trace()
                    self.logger.info("Remove stock %s big drop>criteria...Drop day: %s"%(s,day))
                    tmp.append(s)
                    break
        ret = list(set(stock_list) ^ set(tmp))
        self.logger.info("Found %s stocks after filtering big drop within %s days"%(len(ret),day_num))
        return ret
    
    def get_score_for_stocks(self,stock_list,day_num):
        '''
        根据分数策略获得每个股票的分数。
        '''
        f = open('stock_score.txt','w')
        for s in stock_list:
            score = 0
            name = self.util.get_stock_name_from_id(s)
            for day in range(day_num):
                change = self.util.get_increase_amount(s,day)
                lift = self.util.get_lift_in_one_day(s,day)
                print(change)
                print(lift)
                delta = change*(10+day_num-day)
                print(delta)
                #score = score+change*(10+day_num-day)+lift*(10+day_num-day)
                score = score+change*(10+day_num-day)
                print("Score: %s, day:%s"%(score,day))
            #if score>0:
            ss = "%s:%s:%s\n"%(s,name,score)
            self.logger.info(ss)
            f.write(ss)
        f.close()


if __name__ == '__main__':
    a = StockFilter()
    #s_list = a.util.get_trading_stocks()
    #s_list = ['sz002172', 'sz300163', 'sz000608', 'sz002845', 'sz002199', 'sh601116', 'sz300610', 'sz300586', 'sz002201', 'sz000151', 'sh600844', 'sz000413', 'sh603637', 'sz002112', 'sh600225', 'sz300392', 'sz002862', 'sz002336', 'sz002560', 'sh600112', 'sh600318', 'sh600743', 'sh600962', 'sz300464', 'sz002182', 'sh603696', 'sh600156', 'sh603718', 'sh600143', 'sh600311', 'sz002939', 'sz002726', 'sh601990', 'sh600774', 'sz300692', 'sh603701', 'sz002937', 'sz300116', 'sh601099', 'sz000517', 'sz002423', 'sz300083', 'sz002576', 'sz002209', 'sz002724', 'sz300120', 'sz002178', 'sz300532', 'sh600240', 'sz002857', 'sz002716', 'sh600306', 'sz002633', 'sz300693', 'sh600864', 'sz002211', 'sz300444', 'sz000752', 'sz300281', 'sh603607', 'sz300465', 'sz002940', 'sz300162', 'sh603088', 'sh600211', 'sz002569', 'sz002445', 'sh603669', 'sh600462', 'sh600746', 'sz300643', 'sh600792', 'sz002333', 'sz002708', 'sh601375', 'sh600909', 'sh600355', 'sh600159', 'sz000068', 'sz000031', 'sh600758', 'sz002232', 'sz300279', 'sh603081', 'sz000691', 'sz000780', 'sz002264', 'sz002667', 'sz002575', 'sz002902', 'sz300736', 'sz002760', 'sz000750', 'sz002288', 'sh600768', 'sz000668', 'sz002676', 'sz002839', 'sz002929', 'sh603398', 'sh600621', 'sz000800', 'sh600684', 'sz002059', 'sz000584', 'sz000927', 'sh603725', 'sh601162', 'sh603656', 'sz002762', 'sz002755', 'sz300612', 'sh600173', 'sz002865', 'sz002848', 'sh603811', 'sz300384', 'sz002766', 'sz002797', 'sz002591', 'sz002654', 'sz002504', 'sz000153', 'sz000757', 'sh603076', 'sz300538', 'sz300547', 'sz300167', 'sh600162', 'sz002899', 'sh603078', 'sh600766', 'sh600742', 'sz300492', 'sz300686', 'sz300096', 'sz002803', 'sh600687', 'sh603486', 'sz300409', 'sz002377', 'sh603997', 'sh600250', 'sz000622', 'sz002723', 'sz002909', 'sh601218', 'sz002846', 'sh600249', 'sh603089', 'sz002856', 'sh600369']
    s_list = ['sz300610']
    a.get_score_for_stocks(s_list,5)
    '''
    #5天内有涨停或者接近涨停过
    s_list = a.get_big_increase_within_days(s_list,5,9)
    print(s_list)

    #去掉3天内有大阴线的
    s_list = a.filter_big_drop_within_days(s_list,3,-7)
    print(s_list)
    
    #只取3天内总换手>30%的
    #s_list = a.get_volume_within_days(s_list,3,30)
    #print(s_list)

    #去掉3天内有大阴线形态2的
    s_list = a.filter_big_lift_within_days(s_list,2,-6)
    print(s_list)

    #2天前到现在涨幅>5%
    s_list = a.get_delta_within_days(s_list,2,10)
    print(s_list)
    '''
    