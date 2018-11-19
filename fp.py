import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_filter import StockFilter
from stock_mailer import StockMailer
import time
from stock_db import StockDb

def analyze():
    '''
    To save time, please run pre_analyze first...
    '''
    file_name = "pre_list.csv"
    f = StockFilter()
    s_list = f.util.get_stock_list_from_file(file_name)
    #去掉3天内有大阴线的
    s_list = f.filter_big_drop_within_days(s_list,3,-7)
    print(s_list)
    
    #只取3天内总换手>30%的
    #s_list = f.get_volume_within_days(s_list,3,5)
    #print(s_list)

    #去掉3天内有大阴线形态2的
    s_list = f.filter_big_lift_within_days(s_list,2,-5)
    print(s_list)

    #去掉涨幅变小的
    s_list = f.filter_increase_rate_decrease(s_list,3,3)
    print(s_list)

    #2天前到现在涨幅>5%
    s_list = f.get_delta_within_days(s_list,2,10)
    print(s_list)
    return s_list  


def pre_analyze():
    db = StockDb()
    f = StockFilter()
    s_list = db.get_trading_stock_list()
    print("Found %s stocks for pre check step 1 - get all trading stocks..."%(len(s_list)))
    s_list = f.get_float_shares_below_limit(s_list)  
    print("Found %s stocks for pre check step 2 - get all stocks match float shares criteria"%(len(s_list)))
    s_list = f.filter_new_stocks(s_list)
    print("Found %s stocks for pre check step 3 - remove all stocks which in market in these 2 months"%(len(s_list)))
    return s_list

def get_top_n(s_list,n,day_num):
    print("Try to find top %s in %s days"%(n,day_num))
    f = StockFilter()
    s_list = f.get_big_increase_within_days(s_list,5,9)
    return f.get_top_increase(s_list,n,day_num)

def get_potential(s_list):  #只是获取涨幅变大的而已    
    f = StockFilter()
    s_list = f.get_big_increase_within_days(s_list,5,9)
    s_list = f.get_high_score_list(s_list)
    #print(type(s_list))
    #print(s_list)
    #s_list = f.get_increase_rate_increase(s_list,3) 
    s_list = f.get_delta_within_days(s_list,7,0)
    s_list = f.get_delta_within_days(s_list,5,5)
    s_list = f.get_delta_within_days(s_list,3,10)
    #s_list = f.filter_big_lift_within_days(s_list,3,0)
    return s_list

def get_potential_2(s_list):
    f = StockFilter()   
    s_list = f.get_big_turnover_within_days(s_list,5,5)
    s_list = f.get_high_score_list(s_list)
    s_list = f.get_increase_rate_increase(s_list,3)
    s_list = f.get_delta_within_days(s_list,7,0)
    s_list = f.get_delta_within_days(s_list,5,5)
    #filter_list = f.get_delta_within_days(s_list,3,10)
    #s_list = list(set(s_list)-set(filter_list))
    #s_list = f.filter_low_score_today(s_list)
    return s_list

def compose_and_send(fp_result):
    m = StockMailer()    
    for result in fp_result:
        m.compose_msg_body(result)
    m.send_fp_mail(1)

def update_db(fp_result):
    db = StockDb()
    fp_date = db.get_last_trading_date()
    count = 0
    for result in fp_result:
        db.add_fp_result(result,count,fp_date)
        count = count+1

def fp():   
    pre_list = pre_analyze()
    fp_result = []
    fp_result.append(get_top_n(pre_list,10,8)) # 8日内涨幅前10
    fp_result.append(get_potential(pre_list))
    #fp_result.append(get_potential_2(pre_list))
    update_db(fp_result)
    compose_and_send(fp_result)    

if __name__ == '__main__':    
    s_list = pre_analyze()
    fp()
    #time.sleep(30)
    #send_fp_mail()

    
    
    