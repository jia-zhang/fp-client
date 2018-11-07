import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil
import time
import datetime
from stock_mailer import StockMailer

def get_yesterday(): 
    today=datetime.date.today() 
    oneday=datetime.timedelta(days=1) 
    yesterday=today-oneday  
    return yesterday.strftime('%Y_%m_%d')

def get_today():
    return datetime.date.today().strftime('%Y_%m_%d')

def summarize():
    yesterday = get_yesterday()
    file_name = "output/%s.csv"%(yesterday)
    today = get_today()
    output_file_name = "output/summary_%s.csv"%(today)
    t = StockUtil()
    s_list = t.get_stock_list_from_file(file_name)
    f = open(output_file_name,'w')
    f.write("股票ID，股票名称，当前价格，涨幅，成交手数，成交金额，开盘涨幅\n")
    for s in s_list:
        info = t.get_live_mon_items(s)
        f.write(info)
        f.write('\n')
    f.close()

def send_sum_mail():
    m = StockMailer()
    today = get_today()
    msg_subject = "Summary info - %s"%(today)
    input_file_name = "output/summary_%s.csv"%(today)
    with open(input_file_name,'r') as f:
        msg_body = f.read()
    m.send_mail_to_one_rcpt("jenixe@126.com",msg_subject,msg_body)

if __name__ == '__main__':       
    #monitor(file_name,60)
    #monitor_after_bid(file_name,60)
    summarize()
    send_sum_mail()