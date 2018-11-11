import sys
sys.path.append("./lib")
sys.path.append(".")
from bs4 import BeautifulSoup
import requests 
from stock_db import StockDb
import time

def get_pchange(stock_id):
    ori_stock_id = stock_id
    if stock_id.startswith('sh'):
        stock_id = "0%s"%(stock_id.replace('sh',''))
    else:
        stock_id = "1%s"%(stock_id.replace('sz',''))
    #print(stock_id)
    url = "http://quotes.money.163.com/service/chddata.html?code=%s&start=20181022&end=20181109&fields=PCHG"%(stock_id)
    #print(url)
    r = requests.get(url)
    r_list = r.text.split('\r\n')[1:-1]
    for line in r_list:
        tmp = line.split(',')
        date = tmp[0]
        pchg = round(float(tmp[-1]),2)
        #print("%s:%s:%s"%(ori_stock_id,date,pchg))
        update_pchg(ori_stock_id,date,pchg)
    return r_list

def update_pchg(stock_id,date,pchg):
    db = StockDb()
    sql_cmd = "update tb_daily_info set pchg='%s' where stock_id='%s' and date='%s'"%(pchg,stock_id,date)
    #print(sql_cmd)
    db.update_db(sql_cmd)


def get_new_stock_info(page_num):
    url = "http://vip.stock.finance.sina.com.cn//corp/view/vRPD_NewStockIssue.php?page=%s"%(page_num)
    r = requests.get(url)
    bs = BeautifulSoup(r.content,'lxml')
    trs = bs.table.find_all('tr')
    ret = []
    for tr in trs:
        tds = tr.find_all('td')
        td_list = []
        for td in tds:
            td_text = td.text.lstrip().rstrip().replace('\n','')
            td_list.append(td_text)
        #print(','.join(td_list))
        ret.append(td_list)
    #print(ret)
    return ret[3:]

def add_in_mkt_date(stock_id,in_mkt_date):
    db = StockDb()
    sql_cmd = "update tb_basic_info set in_mkt_date='%s' where stock_id='%s'"%(in_mkt_date,stock_id)
    #print(sql_cmd)
    db.update_db(sql_cmd)

def update_float_shares(stock_id,float_shares):
    db = StockDb()
    sql_cmd = "update tb_basic_info set float_shares='%s' where stock_id='%s'"%(float_shares,stock_id)
    #print(sql_cmd)
    db.update_db(sql_cmd)

def update_stock_name(stock_id,stock_name):
    db = StockDb()
    sql_cmd = "update tb_basic_info set stock_name='%s' where stock_id='%s'"%(stock_name,stock_id)
    #print(sql_cmd)
    db.update_db(sql_cmd)

def test2():
    stocks = get_new_stock_info(1)
    for s in stocks:
        print(s)
        stock_id = s[0]
        if stock_id.startswith('60'):
            stock_id = "%s%s"%('sh',stock_id)
        else:
            stock_id = "%s%s"%('sz',stock_id)
        float_shares = int(s[5])*10000
        update_float_shares(stock_id,float_shares)
        #time.sleep(5)

def test1():
    stocks = get_new_stock_info(1)
    for s in stocks:
        print(s)
        stock_id = s[0]
        if stock_id.startswith('60'):
            stock_id = "%s%s"%('sh',stock_id)
        else:
            stock_id = "%s%s"%('sz',stock_id)
        stock_name = s[2]
        update_stock_name(stock_id,stock_name)
        #time.sleep(5)


def test():
    for i in range(15):
        stocks = get_new_stock_info(i+1)
        #j = 0
        for s in stocks:
            print(s)
            stock_id = s[0]
            if stock_id.startswith('60'):
                stock_id = "%s%s"%('sh',stock_id)
            else:
                stock_id = "%s%s"%('sz',stock_id)
            in_mkt_date = s[4]
            #print(stock_id)
            #print(in_mkt_date)
            #print(stock_id)
            add_in_mkt_date(stock_id,in_mkt_date)
            #print(s)
        time.sleep(5)
        

if __name__ == '__main__': 
    '''
    stock_info = get_new_stock_info(1)
    for s in stock_info:
        print(s)
    '''
    get_pchange('sh600000')
    #print(get_pchange('sz000002'))
    #test1()
    
