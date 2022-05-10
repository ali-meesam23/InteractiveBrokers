from datetime import datetime
import time
# LOCAL
# from _Inputs import INFO
from _Connection import App, start, disconnect
# TESTING PARAMS
import _vars as v

global t
t = 0.1


class Account(App):
    """Account Name Must be Chosen"""
    def __init__(self):
        App.__init__(self)
        # ACCOUNT
        self.account_number = v.ACCOUNT_NUMBER
        self.acc_update = {}
        self.funds = 0
        self.cash = 0
        self.position_dollar = 0
        self.equity = 0
        self.unrlzPNL = 0
        self.buyingPower = 0

    def updateAccountValue(self, key, val,currency, accountName):
        self.acc_update[key] = val
        # print(f"{key}:{val}")
        if key=='AvailableFunds':
            # TOTAL CASH FOR MARGIN ACCOUNT
            self.funds = float(self.acc_update['AvailableFunds'])
        elif key == 'TotalCashBalance':
            # TOTAL CASH FOR CASH BALANCE
            self.cash = float(self.acc_update['TotalCashBalance'])
        elif key=='GrossPositionValue':
            # TOTAL DOLLAR POSITION
            self.position_dollar = float(self.acc_update['GrossPositionValue'])
        elif key=='NetLiquidation':
            # TOTAL EQUITY
            self.equity = float(self.acc_update['NetLiquidation'])
        elif key=='BuyingPower':
            # Buying POWER
            self.buyingPower = float(self.acc_update['BuyingPower'])
        elif key == 'UnrealizedPnL':
            # Open Position PNL
            self.unrlzPNL = float(self.acc_update['UnrealizedPnL'])

    def update_cash(self):
        # SUBSCRIBE
        self.reqAccountUpdates(True, self.account_number)
        time.sleep(t)
        # CANCEL SUBSCRIPTION
        # self.reqAccountUpdates(False, self.account_name)
        # CASH
        return float(self.acc_update['TotalCashBalance'])


def requesting_acc_details(client_id=12):
    acc_app = Account()
    start(acc_app, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=client_id)
    time.sleep(0.15)
    acc_app.reqAccountUpdates(True, acc_app.account_number)
    time.sleep(0.1)
    acc_app.reqAccountUpdates(False, acc_app.account_number)
    disconnect(acc_app)
    return acc_app.acc_update


def get_cash(client_id=11):
    acc_app = Account()
    start(acc_app, accName= v.ACCOUNT_NAME, accType= v.ACCOUNT_TYPE, software = v.SOFTWARE,HOST=v.HOST,PORT=v.PORT, clientId=client_id)
    time.sleep(0.15)
    acc_app.reqAccountUpdates(True, acc_app.account_number)
    time.sleep(0.1)

    """
    if cash:
        with open("CurrentCash.txt",'w') as f:
            f.write(str(cash))
            f.close()
    """
    acc_app.reqAccountUpdates(False, acc_app.account_number)
    # time.sleep(t)
    disconnect(acc_app)
    return acc_app.funds


if __name__ == '__main__':
    # s = datetime.now()
    # app = Account(account_name=v.ACCOUNT_NAME,account_type = v.ACCOUNT_TYPE)
    # # START
    # start(app, accName=app.account_name, accType = app.account_type, clientId=v.CLIENT_ID)
    # print("start")
    # time.sleep(0.1)
    # cash = get_cash(app)
    # print(f"Cash Balance: {cash}")
    # time.sleep(0.1)
    # # print(f"Account Details:\n{requesting_acc_details(app)}")
    # # time.sleep(t)
    # # DISCONNECT
    # disconnect(app)
    # print("Stop")
    # e = datetime.now()
    # print(f"Time Elapsed: {round((e-s).total_seconds(),1)}s")
    print(requesting_acc_details(1234))