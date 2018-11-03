
from lib.stock_dump import StockDump
from lib.stock_filter import StockFilter

def prepare_env():
    s = StockDump()
    s.logger.info("Downloading all valid stock information...")
    s.download_valid_stock_list()
    s.logger.info("Downloading stock dynamic data...")
    #s.download_dynamic_from_url()
    s.logger.info("Downloading stock static data...")
    #s.download_static_from_url()
    s.logger.info("Unzipping files...")    
    #s.unzip_dynamic('./data')
    #s.unzip_static('./data')


if __name__ == '__main__':    
    prepare_env()
    