
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
    s_list = ['sz000633']
    #去掉涨幅变小的
    s_list = f.filter_increase_rate_decrease(s_list,3)
    print(s_list)
    

def test():
    t = StockUtil()
    print(t.check_dynamic_data())

if __name__ == '__main__':    
    #prepare_env()
    #test()
    #pre_analyze()
    
    t = StockUtil()
    s_list = analyze()
    print(s_list)
    #for s in s_list:
    #    print("%s-%s:%s"%(s,t.get_stock_name_from_id(s),t.get_live_aoi(s)))
    
    