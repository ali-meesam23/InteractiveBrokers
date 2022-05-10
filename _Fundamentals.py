from _Connection import App, start, disconnect
from _Contract import stk_contract
import time
# TESTING PARAMS
import _vars as v


class Fundamentals_Data(App):
    def __init__(self):
        App.__init__(self)
    def fundamentalData(self, reqId , data:str):
        super().fundamentalData(reqId, data)
        print(reqId, data)

if __name__ == '__main__':
    app = Fundamentals_Data()
    start(app,v.ACCOUNT_NAME,v.ACCOUNT_TYPE,v.SOFTWARE,clientId=v.CLIENT_ID)
    contract = stk_contract('AAPL')
    app.reqFundamentalData(0,contract,'CalendarReport',[])
    time.sleep(3)
    disconnect(app)