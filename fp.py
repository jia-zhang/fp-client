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

def get_top_n(n,day_num,remove_new_stock=1):
    f = StockFilter()
    pre_list = f.util.get_stock_list_from_file("pre_list.csv") 
    f = StockFilter()
    return f.get_top_increase(pre_list,n,day_num,remove_new_stock)

def get_potential(day_num):  #只是获取涨幅变大的而已
    file_name = "pre_list.csv"
    f = StockFilter()
    pre_list = f.util.get_stock_list_from_file(file_name)
    s_list = f.get_increase_rate_increase(pre_list,day_num) 
    s_list = f.get_delta_within_days(s_list,7,0)
    s_list = f.get_delta_within_days(s_list,5,5)
    s_list = f.get_delta_within_days(s_list,3,10)
    s_list = f.filter_big_lift_within_days(s_list,7,0)
    #print(s_list)   
    #s_list2 = f.get_turnover_burst(pre_list,day_num)
    #print(s_list2)
    #s_list.extend(s_list2)
    return s_list

def get_potential_2(day_num):
    db = StockDb()
    f = StockFilter()    
    trading_stock_list = db.get_trading_stock_list()  
    pre_list = f.util.get_stock_list_from_file("pre_list.csv") 
    s_list = list(set(trading_stock_list)-set(pre_list))
    s_list = f.get_increase_rate_increase(s_list,day_num)
    s_list = f.get_delta_within_days(s_list,7,0)
    s_list = f.get_delta_within_days(s_list,5,5)
    s_list = f.filter_big_lift_within_days(s_list,7,0)
    #s_list = f.get_turnover_burst(s_list,day_num)
    print(s_list)
    return s_list

def fp():
    db = StockDb()
    #print(get_potential_2(5))
    #print(get_potential(5))
    #stock_list = db.get_trading_stock_list()
    #print(get_top_n(stock_list,10,5))    
    full_list = []
    top_n_list = get_top_n(10,8) # 8日内涨幅前10
    potential_list = get_potential(2)
    potential_list_2 = get_potential_2(3)
    print(top_n_list)
    print(potential_list)
    print(potential_list_2)
    m = StockMailer()
    fp_date = db.get_last_trading_date()
    m.add_msg_body("谁是龙头：")
    m.compose_msg_body(top_n_list)
    m.add_msg_body("潜力股列表：")
    m.compose_msg_body(potential_list)
    m.add_msg_body("潜力股列表-ds版：")
    m.compose_msg_body(potential_list_2) 
    try:
        db.add_fp_result(top_n_list,"龙头",fp_date)
        db.add_fp_result(potential_list,"潜力",fp_date)
        db.add_fp_result(potential_list_2,"屌丝潜力",fp_date)           
    except:
        pass
    finally:
        m.send_fp_mail(1)
    

if __name__ == '__main__':    
    #fp()
    fp()
    #time.sleep(30)
    #send_fp_mail()

    
    
    