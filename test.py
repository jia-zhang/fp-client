import sys
sys.path.append("./lib")
sys.path.append(".")
from stock_util import StockUtil

t = StockUtil()
#s_list = t.get_valid_stocks()
s_list = t.get_fp_stock_list()
print(t.get_live_status_list(s_list))
#for s in s_list:
#    t.logger.info(t.get_live_aoi(s))