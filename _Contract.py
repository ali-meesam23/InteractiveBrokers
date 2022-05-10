from ibapi.contract import Contract
from _Connection import App, start, disconnect
import pandas as pd
import time
# TESTING PARAMS
import _vars as v
import os

class InstrumentContract(App):
    """
    App Handler Functions
    """
    def __init__(self):
        App.__init__(self)
        self.contract_details = {}
        # CONTRACT
        self.tickerId = 0
        self.all_contract_info = None

    def contractDetails(self, reqId, contractDetails):
        c = contractDetails
        self.all_contract_info = contractDetails
        self.contract_details["ConId"] = c.contract.conId
        self.contract_details["Ticker"] = c.contract.symbol
        self.contract_details['SecId'] = c.contract.secId
        self.contract_details['validExchanges'] = c.validExchanges
        self.contract_details["longName"] = c.longName
        self.contract_details["industry"] = c.industry
        self.contract_details["category"] = c.category
        self.contract_details["subcategory"] = c.subcategory
        self.contract_details['UnderSymbol'] = c.underSymbol
        self.contract_details['UnderConId'] = c.underConId
        self.contract_details['SecIdList'] = c.secIdList
        self.contract_details['TimeZoneId'] = c.timeZoneId
        self.contract_details['TradingHours'] = c.tradingHours
        self.contract_details['RTH'] = c.liquidHours
        self.tickerId = c.contract.conId


def primary_exhcange(ticker):
    cboe = ['CSCO', 'MSFT','PSFE']
    arca = ['UPRO', 'SPXU']

    if ticker in cboe:
        return "CBOE"
    elif ticker in arca:
        return "ARCA"
    else:
        return "SMART"

def stk_contract(symbol, sec_type="STK", currency="USD", exchange="SMART"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.primaryExchange = primary_exhcange(symbol)
    contract.exchange = exchange
    return contract

def opt_contract(ticker="SPY",option_type='C',strike='450',expiry='20210430'):
    contract = Contract()
    contract.symbol = ticker
    contract.exchange = 'SMART'
    contract.secType = 'OPT'
    contract.strike = str(strike)
    contract.currency = 'USD'
    contract.lastTradeDateOrContractMonth = expiry
    contract.right = option_type
    contract.multiplier = '100'
    return contract

def request_contract(appObj, ticker, primary_exch=None,reqId=0):
    appObj.reqContractDetails(reqId, stk_contract(ticker))

def get_ticker_id(app, ticker,_exchange="SMART"):
    t = 0.5
    TICKER_IDS_CSV = os.getenv("IB_TICKERID_PATH")
    # GET CSV TICKERS ID LIST
    df = pd.read_csv(TICKER_IDS_CSV)
    csv_tickers = list(df.ticker)
    # CHECK FOR TICKERS
    if ticker in csv_tickers:
        tickerId = df[df['ticker'] == ticker]['tickerId'].iloc[0]
        print('Ticker', ticker, "| TickerID:", tickerId)
        return tickerId
    else:
        # REQUEST CONTRACT INFO & GET TICKER ID
        request_contract(app, ticker, _exchange)
        time.sleep(t)

        print('Ticker', ticker, "TickerID:", app.tickerId)
        if app.tickerId != 0:
            df = df.append(pd.DataFrame({'ticker': [ticker], 'tickerId': [app.tickerId]}), ignore_index = True)
        else:
            print(f"{ticker}: Ticker ID Not Found")
            app.tickerId = 0
        # UPDATE CSV
        if csv_tickers != list(df['ticker']):
            df.to_csv(TICKER_IDS_CSV, index=False)
        time.sleep(t)
        return app.tickerId


if __name__=='__main__':
    app = InstrumentContract()
    start(app,v.ACCOUNT_NAME,v.ACCOUNT_TYPE,v.SOFTWARE,clientId=v.CLIENT_ID)
    ticker = v.ticker
    request_contract(app,ticker)
    time.sleep(1)
    print(app.contract_details)
    get_ticker_id(app,ticker)
    time.sleep(1)
    disconnect(app)
