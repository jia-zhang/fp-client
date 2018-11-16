import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_filter import StockFilter
from stock_util import StockUtil
from stock_mailer import StockMailer
import time
import datetime
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
    print("Found %s stocks for pre check step 1..."%(len(s_list)))
    s_list = f.get_float_shares_below_limit(s_list)  
    print("Found %s stocks for pre check step 2..."%(len(s_list)))
    s_list = f.get_mkt_share_below_limit(s_list)      
    print("Found %s stocks for pre check..."%(len(s_list)))
    return s_list

def get_top_n(n,day_num,remove_new_stock=1):
    f = StockFilter()
    pre_list = f.util.get_stock_list_from_file("pre_list.csv") 
    f = StockFilter()
    return f.get_top_increase(pre_list,n,day_num,remove_new_stock)

def get_potential(s_list):  #只是获取涨幅变大的而已    
    f = StockFilter()
    s_list = f.get_big_increase_within_days(s_list,5,9)
    s_list = f.get_increase_rate_increase(s_list,3) 
    s_list = f.get_delta_within_days(s_list,7,0)
    s_list = f.get_delta_within_days(s_list,5,5)
    s_list = f.get_delta_within_days(s_list,3,10)
    s_list = f.filter_big_lift_within_days(s_list,7,0)
    return s_list

def get_potential_2(s_list):
    f = StockFilter()    
    s_list = f.get_increase_rate_increase(s_list,3)
    s_list = f.get_delta_within_days(s_list,7,0)
    s_list = f.get_delta_within_days(s_list,5,5)
    s_list = f.filter_big_lift_within_days(s_list,7,0)
    return s_list

def fp():
    db = StockDb() 
    top_n_list = get_top_n(10,8) # 8日内涨幅前10
    pre_list = pre_analyze()
    potential_list = get_potential(pre_list)
    potential_list_2 = get_potential_2(pre_list)
    print(top_n_list)
    print(potential_list)
    print(potential_list_2)
    m = StockMailer()
    fp_date = db.get_last_trading_date()
    m.add_msg_body("一类：")
    m.compose_msg_body(top_n_list)
    m.add_msg_body("二类：")
    m.compose_msg_body(potential_list)
    m.add_msg_body("三类：")
    m.compose_msg_body(potential_list_2) 
    try:
        db.add_fp_result(top_n_list,0,fp_date)
        db.add_fp_result(potential_list,1,fp_date)
        db.add_fp_result(potential_list_2,2,fp_date)           
    except:
        pass
    finally:
        m.send_fp_mail(0)
    

if __name__ == '__main__':    
    #fp()
    fp()
    #time.sleep(30)
    #send_fp_mail()

    
    
    