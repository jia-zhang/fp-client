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

def get_top_n(n,day_num):
    f = StockFilter()
    pre_list = f.util.get_stock_list_from_file("pre_list.csv") 
    f = StockFilter()
    return f.get_top_increase(pre_list,n,day_num)

def get_potential(day_num):
    file_name = "pre_list.csv"    
    ret = []
    f = StockFilter()
    s_list = f.util.get_stock_list_from_file(file_name)
    s_list = f.get_increase_rate_increase(s_list,day_num)    
    return s_list

def get_potential_2(day_num):
    ret = []
    db = StockDb()
    f = StockFilter()
    
    trading_stock_list = db.get_trading_stock_list()  
    pre_list = f.util.get_stock_list_from_file("pre_list.csv") 
    s_list = list(set(trading_stock_list)-set(pre_list))
    s_list = f.get_increase_rate_increase(s_list,day_num)
    
    #filter volumes...
    #s_list = ['sz002790', 'sz300600', 'sh603578', 'sh600563', 'sh601990', 'sh600550', 'sz300517', 'sh600318', 'sh603901', 'sz300619', 'sh600909', 'sh601882', 'sz002300', 'sh600375', 'sz300370', 'sz300317', 'sz002083', 'sz002748', 'sh603822', 'sz300715', 'sz300162', 'sz300393', 'sh600425', 'sz002650', 'sz300475', 'sh600696', 'sz300374', 'sh600126', 'sh603587', 'sz002922', 'sh601500', 'sz002494', 'sz002597', 'sz300354', 'sh603976', 'sz002797', 'sh603416', 'sz002652', 'sz002899', 'sz300743', 'sz000955', 'sz300680', 'sh603926', 'sz002519', 'sh600817', 'sz300694', 'sh603683', 'sz000815', 'sh600109', 'sh600199', 'sh600589', 'sz002343', 'sz002260', 'sh600234', 'sh603041', 'sz002216', 'sh600460', 'sz002104', 'sh600854', 'sh600478', 'sh600202', 'sz300270', 'sz300569', 'sh600506', 'sz300656', 'sz002788', 'sz002270', 'sh603833', 'sz000560', 'sz000150', 'sh600217', 'sh600098', 'sh600458', 'sh603637', 'sz000523', 'sh601111', 'sh603378', 'sh603557', 'sh600275', 'sz000635', 'sz002646', 'sz002843', 'sh603013', 'sz300536', 'sz300433', 'sh600707', 'sz002926', 'sz002105', 'sz300691', 'sh600421', 'sz000677', 'sz300192', 'sz300499', 'sz300295', 'sz300049', 'sz000809', 'sh600860', 'sz300169', 'sh603839', 'sh601375', 'sh600248', 'sh603586', 'sh600798', 'sz300512', 'sz002322', 'sz300547', 'sz300210', 'sh603709', 'sh603315', 'sz300091', 'sz300157', 'sz002629', 'sh600733', 'sh600122', 'sz002145', 'sh603045', 'sz300418', 'sz002248', 'sz002820', 'sh603696', 'sh601108', 'sz000987', 'sh600851', 'sz300417', 'sh603655', 'sz002136', 'sz300483', 'sz002624', 'sz300592', 'sz002739', 'sh603303', 'sh603266', 'sz002211', 'sz002803', 'sz002785', 'sz002927', 'sh600162', 'sz002883', 'sh600343', 'sz300535', 'sz300554', 'sh600077', 'sh601012', 'sz002591']
    s_list = f.get_turnover_burst(s_list,day_num)
    print(s_list)
    #for s in s_list:
    #    if f.util.get_delta(s,3)<10:
    #        ret.append(s)   
    return s_list
    #print(len(ret))
    #return ret


def add_to_list(full_list, sub_list):
    ret = full_list
    for i in sub_list:
        if i not in ret:
            ret.append(i)
    return ret

def fp():
    db = StockDb()
    #print(get_potential_2(5))
    #print(get_potential(5))
    #stock_list = db.get_trading_stock_list()
    #print(get_top_n(stock_list,10,5))    
    full_list = []
    top_n_list = get_top_n(10,8)
    potential_list = get_potential(5)
    potential_list_2 = get_potential_2(5)
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
        print(m.msg_body_list)
        m.send_fp_mail()
    

if __name__ == '__main__':    
    #fp()
    fp()
    #time.sleep(30)
    #send_fp_mail()

    
    
    