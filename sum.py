import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil
import time
import datetime
from stock_mailer import StockMailer
import pandas as pd

def test():
    data = [['Alex',10],['Bob',12],['Clarke',13]]
    df = pd.DataFrame(data,columns=['Name','Age'])
    h = df.to_html()
    print(h)

def summarize():
    yesterday = get_yesterday()
    file_name = "output/fp_%s.csv"%(yesterday)
    today = get_today()
    output_file_name = "output/summary_%s.csv"%(today)
    t = StockUtil()
    s_list = t.get_stock_list_from_file(file_name)
    f = open(output_file_name,'w')
    f.write("股票名称（股票ID）| 开盘涨幅 | 当前涨幅 | 当前价格 | 成交量（万手）| 成交金额（亿）\n")
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
    test()
    #send_sum_mail()