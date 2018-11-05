
import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_dump import StockDump
from stock_filter import StockFilter
from stock_util import StockUtil
from stock_trade import StockTrade

def prepare_env():
    s = StockDump()
    s.logger.info("Downloading all valid stock information...")
    #s.download_valid_stock_list()
    s.logger.info("Downloading stock dynamic data...")
    s.download_dynamic_from_url()
    s.logger.info("Downloading stock static data...")
    #s.download_static_from_url()
    s.logger.info("Unzipping files...")    
    s.unzip_dynamic('./data')
    #s.unzip_static('./data')

def pre_analyze():
    file_name = "pre_list.csv"
    f = StockFilter()
    s_list = f.util.get_trading_stocks()
    s_list = f.get_big_increase_within_days(s_list,5,9)
    if len(s_list)>0:
        result = ','.join(s_list)
    with open(file_name,'w') as f:
        f.write(result)
    #print(s_list)

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
    #s_list = a.get_volume_within_days(s_list,3,30)
    #print(s_list)

    #去掉3天内有大阴线形态2的
    s_list = f.filter_big_lift_within_days(s_list,2,-6)
    print(s_list)

    #2天前到现在涨幅>5%
    s_list = f.get_delta_within_days(s_list,2,10)
    print(s_list)
    return s_list    


def test():
    t = StockUtil()
    print(t.check_dynamic_data())

if __name__ == '__main__':    
    prepare_env()
    #test()
    #pre_analyze()
    '''
    t = StockUtil()
    s_list = analyze()
    for s in s_list:
        print("%s-%s:%s"%(s,t.get_stock_name_from_id(s),t.get_live_aoi(s)))
    '''
    