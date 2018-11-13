
import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_dump import StockDump
from stock_filter import StockFilter
from stock_db import StockDb

def pre_analyze():
    file_name = "pre_list.csv"
    db = StockDb()
    f = StockFilter()
    s_list = db.get_trading_stock_list()
    s_list = f.get_big_increase_within_days(s_list,5,9)
    print("Found %s stocks for pre check..."%(len(s_list)))
    if len(s_list)>0:
        result = ','.join(s_list)
    with open(file_name,'w') as f:
        f.write(result)
    #print(s_list)

if __name__ == '__main__':        
    pre_analyze()
    
    
    