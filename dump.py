import sys
sys.path.append("./lib")
sys.path.append(".")
from lib.stock_dump import StockDump
import os
import time


def dump_stock():
    s = StockDump()
    s.logger.info("start")
    s.dump_stock_dynamic(240,15)
    s.zip_dynamic('./data/dynamic')
    #time.sleep()
    s.upload_dynamic('s3://g1-build/tmp')


if __name__ == '__main__':    
    if not os.path.exists("./data"):
        os.makedirs("./data")
    if not os.path.exists("./data/dynamic"):
        os.makedirs("./data/dynamic")
    dump_stock()
    