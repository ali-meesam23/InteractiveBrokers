import pandas_datareader.data as web
from datetime import datetime, timedelta
from _Connection import start, disconnect
from _Contract import InstrumentContract, opt_contract, stk_contract, get_ticker_id
import time
# TESTING PARAMS
import _vars as v


class Ticker_SnapShot(InstrumentContract):
    def __init__(self):
        InstrumentContract.__init__(self)
        self.tick_price = 0
        self.ticker_id = 0

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        # print(reqId, tickType, price, attrib)
        print("CODE:", self.error_code)
        if price != 0 and (tickType in [4, 9]):
            self.tick_price = price
            time.sleep(0.5)

        if self.error_code == 200:

            self.tick_price = 0

    def tickSnapshotEnd(self, reqId: int):
        super().tickSnapshotEnd(reqId)
        print("TickSnapshotEnd. TickerId:", reqId)

    def tickByTickMidPoint(self, reqId: int, time: int, midPoint: float):
        super().tickByTickMidPoint(reqId,time,midPoint)
        self.tick_price = midPoint

    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float,
                          size: int, tickAttribLast, exchange: str,
                          specialConditions: str):
        super().tickByTickAllLast(reqId, tickType, time, price, size, tickAttribLast, exchange, specialConditions)
        if tickType == 1:
            print("Last.", end = " ")
        else:
            print("AllLast.", end = " ")
        print(reqId, datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S"), "Price:", price, "Size:",size, "Exch:", exchange,"PastLimit:",tickAttribLast.pastLimit,"Unreported:", tickAttribLast.unreported)
        self.tick_price = price


def ticker_price(ticker):
    """:key get the latest ticker price"""
    try:
        last_price = web.DataReader(ticker.upper(), 'yahoo',
                                    start = datetime.today() - timedelta(days = 1.0))[
            'Adj Close'].iloc[-1]
        # print(f"TYPE:{type(last_price)}")
        if not last_price:
            return 0
        else:
            return last_price
    except:
        print(f"Failed to retrieve information for {ticker}")
        last_price = 0
        return last_price


def ticker_snapshot(app, req_id, ticker,type='stk',option_type='C',strike=None,expiry = None):
    t = 0.5
    if type=='opt':
        contract = opt_contract(ticker,option_type,strike,expiry)
        time.sleep(t)
        app.reqContractDetails(req_id, contract)
        time.sleep(t)
    else:
        contract = stk_contract(ticker)
        time.sleep(t)
        app.ticker_id = get_ticker_id(app, ticker)
    time.sleep(t)

    # print("CONTRACT:", app.contract_details)
    time.sleep(2*t)
    app.reqMktData(app.ticker_id, contract, "", True, False, [])
    time.sleep(5*t)
    app.cancelMktData(app.ticker_id)
    time.sleep(t)

    # print('ticker ID:', app.ticker_id)
    print(f"{ticker}: ${app.tick_price}")
    time.sleep(t)
    return app.tick_price


if __name__ == "__main__":
    # USING PANDAS DATAREADER FOR STOCKS ONLY
    # print(ticker_price("NFLX"))

    # USING IB
    app = Ticker_SnapShot()
    start(app,v.ACCOUNT_NAME,v.ACCOUNT_TYPE,v.SOFTWARE,v.CLIENT_ID)
    # INPUT
    tickers = v.tickers
    # UPDATE TICKER IDS
    t_ids = [get_ticker_id(app, ticker) for ticker in tickers]
    type = v._type  # stk/opt
    # USE FOR OPTIONS ONLY
    opt_type = v.opt_type  # C/P
    strike = '420.0'  # String but Float Representation
    expiry = '20210423'  # YYYYMMDD

    snaps = {}
    for i, ticker in enumerate(tickers):
        ################################
        s = datetime.now()
        ################################
        print(i)
        # MARKET DATA
        snap = ticker_snapshot(app, i, ticker = ticker, type = type, option_type = opt_type, strike = strike, expiry = expiry)
        # if type=='stk':
            # MIDPOINT
            # snap = app.reqTickByTickData(i,stk_contract(ticker),'MidPoint',0,False)
            # ALL LAST
            # snap =app.reqTickByTickData(i,stk_contract(ticker),'AllLast',0,False)
            # time.sleep(1)
        if snap != 0:
            snaps[ticker] = snap
        ################################
        e = datetime.now()
        app.tick_price = 0
        print(f"Time Elapsed: {e - s}")
    disconnect(app)
    time.sleep(1)
    print("SNAPSHOT:\n", snaps)
