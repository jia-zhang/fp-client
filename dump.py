
from lib.stock_dump import StockDump


def dump_stock():
    s = StockDump()
    s.logger.info("start")
    s.dump_stock_dynamic(240,15)
    s.zip_dynamic('./data/dynamic')
    s.upload_dynamic('s3://g1-build/tmp')


if __name__ == '__main__':    
    dump_stock()
    