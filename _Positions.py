from _Connection import App, start, disconnect
from _Orders import placeOrder
import time
import pandas as pd
# TESTING PARAMS
import _vars as v

pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 2000)
pd.set_option('max_rows', 250)


class Positions(App):
    """
    App Handler Functions
    """
    def __init__(self):
        App.__init__(self)
        # POSITION
        self.positions_df = pd.DataFrame(columns = ['Account', 'Symbol', 'SecType','Right', 'Currency', 'Position', 'AvgCost','TotalCost'])

    # POSITION
    def position(self, _account, contract, position, avgCost):
        super().position(_account, contract, position, avgCost)
        dictionary = {"Account": _account, "Symbol": contract.symbol,
                      "SecType": contract.secType, "Right":contract.right, 
                      "Currency": contract.currency,
                      "Position": position, "AvgCost": float(avgCost),
                      'TotalCost': float(position)*float(avgCost)
                      }
        if int(position)!=0:
            self.positions_df = self.positions_df.append(dictionary, ignore_index=True)
            time.sleep(0.01)
            self.positions_df = self.positions_df[~self.positions_df.Symbol.duplicated(keep='last')]

    def positionEnd(self):
        super().positionEnd()
        time.sleep(0.5)
        print("PositionEnd")


def get_positions(client_id:int=7):
    '''
    :param account_name:
    :param account_type:
    :param client_id: an ID to run the application for checking positions
    :return: dataframe of all open and today's closed positions
    '''
    posApp = Positions()
    
    start(posApp, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=client_id)
    time.sleep(0.3)
    
    # SUBSCRIBE
    posApp.reqPositions()
    time.sleep(0.5)
    # CANCEL SUBSCRIPTION
    posApp.cancelPositions()
    time.sleep(0.1)
    positions = posApp.positions_df
    disconnect(posApp)
    print("+"*30)
    print(positions)
    print("+"*30)
    return positions


def closeTicker(account_name,account_type,ticker):
    client_id = 999
    pos_df = get_positions(account_name,account_type,client_id=client_id)
    client_id+=1
    if len(pos_df)>0:
        if ticker in pos_df.Ticker.tolist():
            pos = pos_df[pos_df.Ticker==ticker]
            position_size = int(pos.Position)
            direction = 'Buy' if position_size<=0 else "Sell"
            pkg = {
            'account':account_name,
            'account_type':account_type,
            'clientId':client_id,
            'ticker': ticker,
            'direction': direction,
            'quantity': abs(position_size),
            'price': 0,
            'orderType':'market'
            }
            placeOrder(**pkg)
        else:
            print("Ticker not found in open Positions")
    else:
        print("0 Positions found")


def closeShop(account_name, account_type):
    """
    !!!!! Close all positions on market !!!!!!
    """
    client_id = 888
    pos_df = get_positions(account_name,account_type,client_id=client_id)
    pos_df = pos_df[pos_df.Position!=0]
    for i in range(len(pos_df)):
        client_id +=i
        pos = pos_df.iloc[i]
        ticker = pos.Symbol
        position_size = int(pos.Position)
        direction = 'Buy' if position_size<=0 else "Sell"
        pkg = {
        'account':account_name,
        'account_type':account_type,
        'clientId':client_id,
        'ticker': ticker,
        'direction': direction,
        'quantity': abs(position_size),
        'price': 0,
        'orderType':'market'
        }
        placeOrder(**pkg)
        time.sleep(0.5)


if __name__ == "__main__":
    position_df = get_positions(10)
    print(position_df)