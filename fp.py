import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_filter import StockFilter
from stock_util import StockUtil
from stock_mailer import StockMailer
import time
import datetime

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

def get_top_n():
    file_name = "pre_list.csv"
    f = StockFilter()
    s_list = f.util.get_stock_list_from_file(file_name)
    s_list = f.get_top_increase(s_list,10,7)
    return s_list

def get_potential():
    file_name = "pre_list.csv"
    f = StockFilter()
    s_list = f.util.get_stock_list_from_file(file_name)
    s_list = f.get_increase_rate_increase(s_list,3)
    return s_list


def fp():
    m = StockMailer()
    t = StockUtil()
    s_list = analyze()    
    #for s in s_list:
    #    print("%s-%s:%s"%(s,t.get_stock_name_from_id(s),t.get_live_aoi(s)))  
    file_name = "./output/fp_%s.csv"%(t.get_today())  
    t.save_stock_list_to_file(s_list,file_name)
    m.send_fp_mail(s_list)

def fp1():
    top_n_list = get_top_n()
    potential_list = get_potential()
    print(top_n_list)
    print(potential_list)
    m = StockMailer()
    m.add_msg_body("谁是龙头：")
    m.compose_msg_body(top_n_list)
    m.add_msg_body("潜力股列表：")
    m.compose_msg_body(potential_list)
    print(m.msg_body_list)

if __name__ == '__main__':    
    #fp()
    fp1()
    #time.sleep(30)
    #send_fp_mail()

    
    
    