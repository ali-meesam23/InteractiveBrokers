import pandas_datareader.data as web
from datetime import datetime, timedelta

# IMPORTS
from _Connection import start, disconnect
import time
from _Account import Account, get_cash
from _Orders import openOrderCashValue


### PERC TO CASH

def percToCash(account_name:str, account_type:str, perc:int):
    """
    perc: 1 - 100
    """
    if perc > 100:
        perc = 100

    minimum_cash = 5000  # Minimum tradeSize
    minimum_balance = 1000  # Minimum Account Balance

    # APPS INIT
    accApp = Account(account_name, account_type)

    start(accApp, accName = accApp.account_name, accType = accApp.account_type, clientId = 100)
    time.sleep(0.1)

    actualCash = get_cash(accApp)
    time.sleep(0.1)

    disconnect(accApp)

    print(f"Total Cash Incl. Open Orders: ${actualCash}")

    cashAfterOpenOrders = actualCash - openOrderCashValue(accApp.account_name, accApp.account_type)

    # Total Cash In the Account
    cashForTrade = cashAfterOpenOrders * perc / 100

    print(f"Cash Available for the Trade: ${int(cashForTrade)}")

    accBalAftTrd = cashAfterOpenOrders - cashForTrade
    # ENFORCING MINIMUM TRADESIZE(cash)
    if (cashForTrade < minimum_cash) and ((cashAfterOpenOrders - minimum_cash) > minimum_balance):
        cashForTrade = minimum_cash
        print(f"TradeSize Updated: ${cashForTrade}")
        accBalAftTrd = cashAfterOpenOrders - minimum_cash

    # 'DO NOT PLACE A TRADE IF THESE CONDITIONS ARE MET'

    if (accBalAftTrd - minimum_balance) < 0:
        print("No enough Balance For Placing this Trade")
        return 0

    elif cashForTrade < minimum_cash:
        print("Trade Size Lower Than Min. Trade Size")
        return 0
    else:
        return cashForTrade


def cashToQuantity(ticker:str,cash:float,tkrprice=None):
    """:param ticker and cash"""
    # ===============GET THE LATEST PRICE (MARK)===============
    if not tkrprice:
        try:
            tkrprice = web.DataReader(ticker.upper(), 'yahoo', start=datetime.today()-timedelta(days=10))['Adj Close'].iloc[-1]
        except:
            print(f"Failed to retrieve information for {ticker}")
            tkrprice = 0
        
    qty = cash // tkrprice if tkrprice != 0 else 0
    return qty, round(tkrprice,2)


def quantityToCash(ticker,qty, tkrprice=None):
    if not tkrprice:
        try:
            tkrprice = web.DataReader(ticker.upper(), 'yahoo', start=datetime.today() - timedelta(days=10))['Adj Close'].iloc[-1]
        except:
            print(f"Failed to retrieve information for {ticker}")
            tkrprice = 0
    cash = qty * tkrprice
    return cash, round(tkrprice,2)


if __name__ == '__main__':
    # TESTING CODE
    tradeCash = percToCash("Meesam", 'Real', 5)
