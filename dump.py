import sys
sys.path.append('./lib')
from lib.stock_dump import StockDump

def dump():       
    t = StockDump()
    #t.get_last_trading_date_live()
    confirm = input("Do pre dump?")
    if confirm=='y':
        t.pre_dump()
    confirm = input("Check diff?")
    if confirm=='y':
        t.check_diff()
    confirm = input("Continue to add data to database?")
    if confirm=='y':
        t.update_db()

if __name__ == '__main__':
    dump()