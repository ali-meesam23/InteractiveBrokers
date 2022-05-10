""" Create and Place Orders """;

from ibapi.order import Order
from _Connection import App, start, disconnect
from _Contract import stk_contract
import pandas as pd
import time
from datetime import datetime
# TESTING PARAMS
import _vars as v
from market_calls import Market


pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 2000)
pd.set_option('max_rows', 250)


class Order_Mgmt(App):
    def __init__(self):
        App.__init__(self)
        # ORDER
        self.nextValidOrderId = 0  # GET THE NEXT VALID ORDER ID FOR EXECUTION
        # ORDER
        self.order_df = pd.DataFrame(
            columns = ['PermId', 'ClientId', 'OrderId', 'Account', 'Symbol', 'SecType', 'Exchange', 'Action',
                       'OrderType', 'TotalQty', 'CashQty', 'LmtPrice', 'AuxPrice', 'Status'])

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        # print(">>>> NextValidId Callback:", orderId)

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        dictionary = {"PermId": order.permId, "ClientId": order.clientId, "OrderId": orderId,
                      "Account": order.account, "Symbol": contract.symbol, "SecType": contract.secType,
                      "Exchange": contract.exchange, "Action": order.action, "OrderType": order.orderType,
                      "TotalQty": order.totalQuantity, "CashQty": order.cashQty,
                      "LmtPrice": order.lmtPrice, "AuxPrice": order.auxPrice, "Status": orderState.status}
        self.order_df = self.order_df.append(dictionary, ignore_index=True)


def orderWithTrailStop(parentOrderId, action, quantity,limitPrice, stopPerc=None):
    action = action.upper()
    #This will be our main or "parent" order
    parent = Order()
    parent.orderId = parentOrderId
    parent.action = action
    parent.orderType = "LMT"
    parent.totalQuantity = quantity
    parent.lmtPrice = limitPrice
    #The parent and children orders will need this attribute set to False to prevent accidental executions.
    #The LAST CHILD will have it set to True, 
    parent.transmit = False

    order = Order()
    order.orderId = parent.orderId + 1
    order.action = "SELL" if action == "BUY" else "BUY"
    order.orderType = "TRAIL"
    order.totalQuantity = quantity
    order.trailingPercent = stopPerc # from 0 to 100
    order.parentId = parentOrderId
    order.transmit = True
    
    bracket_order = [parent, order]
    return bracket_order


def bracketOrder(parentOrderId, action, quantity,limitPrice, takeProfitLimitPrice=None, stopLossPrice=None):
    action = action.upper()
    #This will be our main or "parent" order
    parent = Order()
    parent.orderId = parentOrderId
    parent.action = action
    parent.orderType = "LMT"
    parent.totalQuantity = quantity
    parent.lmtPrice = limitPrice
    parent.algoStrategy = 'DarkIce'
    #The parent and children orders will need this attribute set to False to prevent accidental executions.
    #The LAST CHILD will have it set to True, 
    parent.transmit = False

    if takeProfitLimitPrice:
        takeProfit = Order()
        takeProfit.orderId = parent.orderId + 1
        takeProfit.action = "SELL" if action == "BUY" else "BUY"
        takeProfit.orderType = "LMT"
        takeProfit.totalQuantity = quantity
        takeProfit.lmtPrice = takeProfitLimitPrice
        takeProfit.parentId = parentOrderId
        takeProfit.transmit = False if stopLossPrice else True
    else:
        takeProfit = None
    
    if  stopLossPrice:
        stopLoss = Order()
        stopLoss.orderId = parent.orderId + 2
        stopLoss.action = "SELL" if action == "BUY" else "BUY"
        stopLoss.orderType = "STP"
        #Stop trigger price
        stopLoss.auxPrice = stopLossPrice
        stopLoss.totalQuantity = quantity
        stopLoss.parentId = parentOrderId
        #In this case, the low side order will be the last child being sent. Therefore, it needs to set this attribute to True 
        #to activate all its predecessors
        stopLoss.transmit = True
    else:
        stopLoss = None
    
    bracket_order = []
    for o in [parent,takeProfit, stopLoss]:
        if o:
            bracket_order.append(o)

    # bracket_order = [parent, takeProfit, stopLoss]
    return bracket_order


def limitOrder(direction, quantity, price, **kwargs):
    order = Order()
    order.action = direction
    order.orderType = "LMT"
    order.totalQuantity = quantity
    order.lmtPrice = price
    order.tif = 'DAY'
    return order


def darkIceOrder(direction,quantity,price,**kwargs):
    baseOrder = limitOrder(direction,quantity, price)
    baseOrder.algoStrategy = 'DarkIce'
    return baseOrder


def marketOrder(direction, quantity,**kwargs):
    order = Order()
    order.action = direction
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return order


def stopOrder(direction, quantity, stopPrice,**kwargs):
    order = Order()
    order.action = direction
    order.orderType = "STP"
    order.totalQuantity = quantity
    order.auxPrice = stopPrice
    return order

def trailStopOrder(direction, quantity, tr_perc,**kwargs):
    """
    tr_perc: [0,100] percentage >> use %ATR
    """
    order = Order()
    order.action = direction
    order.orderType = "TRAIL"
    order.totalQuantity = quantity
    order.trailingPercent = tr_perc
    return order

def openOrders_callback(app):
    app.reqAllOpenOrders()
    time.sleep(0.3)
    return app.order_df[~app.order_df.duplicated(keep='last')]

def getAllOpenOrders(account, accountType, clientId):
    app = Order_Mgmt()
    start(app, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=clientId)
    app.reqAllOpenOrders()
    time.sleep(0.2)
    disconnect(app)
    return app.order_df[~app.order_df.duplicated(keep='last')]


def orderPrep(app, tkr_contract, tkr_order):
    """:key Get order id and place order"""
    order_id = app.nextValidOrderId
    app.placeOrder(order_id, tkr_contract, tkr_order)
    time.sleep(0.3)
    app.reqIds(-1)
    app.order_df = app.order_df[~app.order_df.duplicated(keep='last')]
    print(f"Order Placed: ({tkr_contract.symbol}|{tkr_order.action}|{tkr_order.totalQuantity}|@ ${tkr_order.lmtPrice})")


def place_orderWithTrailStop(account,account_type, ticker,direction, quantity, limitPrice, stopPerc,clientId=88):
    app = Order_Mgmt()
    start(app, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=clientId)
    tkr_contract = stk_contract(ticker.upper())
    
    order_id = app.nextValidOrderId
    direction = direction.upper()
    bracket = orderWithTrailStop(order_id, direction, quantity, limitPrice, stopPerc)
    for o in bracket:
        app.placeOrder(o.orderId, tkr_contract, o)
        time.sleep(0.3)    
        app.order_df = app.order_df[~app.order_df.duplicated(keep='last')]
        print(f"Order Placed: ({tkr_contract.symbol}|{direction}|{quantity}|@ ${o.lmtPrice}) Trail: {stopPerc}%")
    app.reqIds(-1) 
    time.sleep(0.1)
    disconnect(app)


def place_bracketOrder(account,account_type, ticker,direction, quantity, limitPrice, takeProfitLimit=None, stopLossLimit=None,clientId=99):
    try:
        app = Order_Mgmt()
        start(app, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=clientId)
        tkr_contract = stk_contract(ticker.upper())
        
        order_id = app.nextValidOrderId
        direction = direction.upper()
        bracket = bracketOrder(order_id, direction, quantity, limitPrice, takeProfitLimit, stopLossLimit)
        for o in bracket:
            app.placeOrder(o.orderId, tkr_contract, o)
            time.sleep(0.3)    
            app.order_df = app.order_df[~app.order_df.duplicated(keep='last')]
            print(f"Order Placed: ({tkr_contract.symbol}|{direction}|{quantity}|@ ${limitPrice}) Bracket: ${takeProfitLimit} / ${stopLossLimit}")
        app.reqIds(-1) 
        time.sleep(0.1)
        disconnect(app)
        return 1
    except:
        return 0


def placeOrder(ticker,direction,quantity, price:float=None, orderType='market',clientId=10):
    """
    pkg = {
    'clientId':5,
    'ticker': 'NKLA',
    _type: stk | perc | dollar
    'direction': 'Buy', 'Sell'
    'quantity': 80,
    'price': 30,
    'orderType':['darkice','market','limit']
    }
    """
    orderApp = Order_Mgmt()
    start(orderApp, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=clientId)
    orderType = orderType.lower()
    if orderType=='market':
        tkr_order = marketOrder(direction,quantity)
    elif orderType=='limit':
        tkr_order = limitOrder(direction,quantity,price)
    elif orderType == 'darkice':
        tkr_order = darkIceOrder(direction,quantity,price)
    elif orderType == 'trailstop':
        tr_perc = 5
        tkr_order = trailStopOrder(direction,quantity,tr_perc)
    else:
        return 'Order Type Unknown!'

    time.sleep(0.1)
    tkr_contract = stk_contract(ticker.upper())
    time.sleep(0.1)
    orderPrep(orderApp,tkr_contract,tkr_order)
    time.sleep(0.1)
    disconnect(orderApp)
    return f'Order Placed: {ticker} {direction} {quantity} @ {orderType}'


def cancelAllOpenOrders(clientId=777):
    app = Order_Mgmt()
    start(app, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=clientId)
    time.sleep(0.1)
    app.reqGlobalCancel()
    time.sleep(0.1)
    print("!!! All Open Orders Cancelled!!!")
    disconnect(app)


def openOrderCashValue(account, accountType,clientId=31):

    # GET TOTAL CASH OUT for each order
    order_df = getAllOpenOrders(account,accountType,clientId=clientId)

    openOrderCash = 0
    for i in range(len(order_df)):
        order_i = order_df.iloc[i]
        # ONLY COUNT FOR BUY ORDERS
        if order_i.Action=='BUY':
            if order_i.CashQty==0:
                openOrderCash += (float(order_i.TotalQty) * float(order_i.LmtPrice))
            else:
                openOrderCash += order_i.cashQty
    return openOrderCash


def cancelTkrOrder(account,accountType, ticker,clientId=3):
    app = Order_Mgmt()
    start(app, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=clientId)
    time.sleep(0.1)
    # GET ALL OPEN ORDERS
    app.reqAllOpenOrders()
    time.sleep(0.1)
    app.order_df = app.order_df[~app.order_df.duplicated(keep='last')]
    open_orders = app.order_df
    if len(open_orders)>0:
        for i in range(len(open_orders)):
            if ticker == open_orders['Symbol'].iloc[i]:
                OrderId = open_orders.iloc[i]['OrderId']
                client_id = int(open_orders.iloc[i]['ClientId'])
                cancelOrderApp = Order_Mgmt()
                start(cancelOrderApp, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=clientId)
                time.sleep(0.1)
                cancelOrderApp.cancelOrder(OrderId)
                time.sleep(0.3)
                disconnect(cancelOrderApp)
                app.reqAllOpenOrders()
                time.sleep(0.1)
                order_cancelled = app.order_df[["Symbol", "Action", "OrderType", "TotalQty", "CashQty", "LmtPrice"]].iloc[i]
                print(f"Order Cancelled:\n{order_cancelled}")
    disconnect(app)


if __name__=='__main__':
    # ACTIONS
    PLACING_ORDER = False
    cancel_ticker_order = False
    cancel_all_orders = True
    #######################################################
    if PLACING_ORDER:
        # MARKET ORDER PACKAGE
        pkgs = v.pkgs
        app = Order_Mgmt()
        start(app,v.ACCOUNT_NAME,v.ACCOUNT_TYPE,v.SOFTWARE,clientId=v.CLIENT_ID)
        for i in pkgs:
            pkg = pkgs[i]
            tkr_contract = stk_contract(pkg['ticker'])
            time.sleep(0.5)
            tkr_order = marketOrder(**pkg)
            # tkr_order = darkIceOrder(**pkg)
            # tkr_order = limitOrder(**pkg)
            time.sleep(0.5)
            orderPrep(app, tkr_contract, tkr_order)
            time.sleep(0.5)  # DISCONNECT APP
        disconnect(app)
    #######################################################
    # CANCEL OPEN ORDERS FOR A TICKER
    if cancel_ticker_order:
        s = datetime.now()
        cancelTkrOrder(v.ACCOUNT_NAME,v.ACCOUNT_TYPE,clientId = v.CLIENT_ID, ticker = v.ticker)
        e = datetime.now()
        print(f"Time Elapsed: {round((e - s).total_seconds(), 1)}s")

    #######################################################
    # SHOW ALL OPEN ORDERS
    print(getAllOpenOrders(v.ACCOUNT_NAME,v.ACCOUNT_TYPE,clientId = v.CLIENT_ID))
    time.sleep(0.5)
    #######################################################
    # CANCEL ALL OPEN ORDERS
    if cancel_all_orders:
        cancelAllOpenOrders(v.ACCOUNT_NAME,v.ACCOUNT_TYPE,clientId = v.CLIENT_ID)
        time.sleep(3)
        #######################################################
        # SHOW ALL OPEN ORDERS
        print(getAllOpenOrders(v.ACCOUNT_NAME,v.ACCOUNT_TYPE,clientId = v.CLIENT_ID))
    #######################################################
    print('Cash Value:',openOrderCashValue(v.ACCOUNT_NAME,v.ACCOUNT_TYPE,clientId = v.CLIENT_ID))
