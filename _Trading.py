
from _TradeBotHelper import *
# IB IMPORTS
from _Positions import get_positions
from _Orders import placeOrder, cancelTkrOrder
import _vars as v

def tradeBot(account, account_type, ticker, direction:str, quantity:int, price=None, unit= 'perc', orderType= 'limit', clientId=10, **kwargs):
    """
    LONG Positions only ->> NO SHORTING (LONF ONLY)
    :param ticker: Stock ticker
    :param quantity: TradeSize
    :param unit: {perc, qty, cash}
    :param direction: (Buy or Sell or Close)
    :return: Flask String to Print
    """
    """
    pkg = {
    'account':"Meesam",
    'account_type':'Real',
    'clientId':5,
    'ticker': 'NKLA',
    'direction': 'Buy',
    'quantity': 80,
    'price': 30,
    'orderType':'DarkIce'
    }
    """
    direction= direction.title()
    if price:
        tkrprice = price
    else:
        tkrprice = None
    # GET tickerPrice, quantity, cash
    if unit=='cash':
        qty, tkrprice = cashToQuantity(ticker, quantity, tkrprice)
        # Change unit to qty
        unit='qty'
        cash = quantity
    elif unit == 'qty':
        cash, tkrprice = quantityToCash(ticker, quantity, tkrprice)
        qty = quantity
    elif unit == 'perc':
        cash = percToCash(account, account_type, quantity)
        qty, tkrprice = cashToQuantity(ticker,cash)
    else:
        qty = 0
        return "Invalid PKG{...}"

    if qty==0:
        return f'Quantity: {qty} >> ERROR!'
    # UPDATING PRICE
    if price:
        if round(price,1) != round(tkrprice,1) and tkrprice not in [0,'nan',None]:
            price = tkrprice
    else:
        price = round(tkrprice,2)

    # IF SIGNAL==CLOSE >> CLOSE ALL POSITION
    # IF SIGNAL==SELL
    #     >> GIVEN QTY - CLOSE GIVEN QUANTITY - CLOSE TILL 0
    #     >> GIVEN PERC - CLOSE PERC OF THE POSITION

    # CLOSE ALL OPEN POSITIONS FOR THE TICKER - >> Using Default ClientId=3
    cancelTkrOrder(account, account_type, ticker)

    if direction.lower() in ['close', 'sell']:
        # GET POSITIONS
        position_df = get_positions(account, account_type)
        if ticker in position_df.Symbol.tolist():
            positionSize = position_df[position_df.Symbol == ticker].Position.sum()
            if direction == "Close":
                # Update direction
                direction = "Sell"
                # Update quantity
                qty = positionSize
                # PLACE TRADE
                return placeOrder(account, account_type, ticker, direction, qty, price, orderType, clientId)
            elif direction == 'Sell':
                if qty > positionSize:
                    qty = positionSize
                return placeOrder(account, account_type, ticker, direction, qty, price, orderType, clientId)
        else:
            return f"Ticker: {ticker} Position Not Found ..."

    else:
        return placeOrder(account, account_type, ticker, direction, qty, price, orderType, clientId)


if __name__=="__main__":
    tradeBot(
        account=v.ACCOUNT_NAME,
        account_type=v.ACCOUNT_TYPE,
        ticker=v.ticker,
        direction=v.direction,
        price= v.price,
        quantity=v.quantity,
        unit=v.orderUnit,
        orderType=v.orderType,
        clientId=v.orderClientId
    )
