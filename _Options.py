# IB IMPORTS
from _Connection import start, disconnect
from _Contract import InstrumentContract, get_ticker_id
from _Orders import Order_Mgmt
# BUILTIN IMPORTS
import time
# TESTING PARAMS
import _vars as v


class OptionsApp(InstrumentContract,Order_Mgmt):
    """
        App Handler Functions
        """
    def __init__(self):
        # App.__init__(self)
        InstrumentContract.__init__(self)
        Order_Mgmt.__init__(self)

        # EXPIRY LIST
        self.expiry_list = []
        # STRIKE LIST
        self.strike_prices = []

    def securityDefinitionOptionParameter(self, reqId: int, exchange: str, underlyingConId: int, tradingClass: str,
                                          multiplier: str, expirations, strikes):
        """:key -> List of expiries and strikes available to the contract"""
        super().securityDefinitionOptionParameter(reqId, exchange, underlyingConId, tradingClass, multiplier,
                                                  expirations, strikes)
        print("Exchange:", exchange, "Expirations:", expirations, "Strikes:", str(strikes))
        self.expiry_list.append(expirations)
        self.strike_prices.append(strikes)


def reqOption_all_Strike_Expiry(appObj, reqId, ticker, ticker_exch = "SMART"):
    _id = get_ticker_id(appObj,ticker,ticker_exch)
    time.sleep(0.1)
    appObj.reqSecDefOptParams(reqId, ticker, "", 'STK', _id)


if __name__ == '__main__':
    # PROGRAM INPUTS
    req_id = v.reqId
    ticker = v.ticker
    ticker_exch = v.exch
    # INITIALIZE
    app = OptionsApp()
    # START
    start(app,v.ACCOUNT_NAME,v.ACCOUNT_TYPE,v.SOFTWARE,clientId=v.CLIENT_ID)
    # REQUEST ALL STRIKES AND EXPIRY DATES
    reqOption_all_Strike_Expiry(app, req_id, ticker, ticker_exch)
    time.sleep(2)
    _strikes = app.strike_prices
    expiries = app.expiry_list
    disconnect(app)
    print("*" * 100)
    print(_strikes)
    print(expiries)

