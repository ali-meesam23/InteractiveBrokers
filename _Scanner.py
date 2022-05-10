from _Connection import App, start, disconnect
import time
# TESTING PARAMS
from _vars import *


class MarketScanner(App):
    def __init__(self):
        App.__init__(self)

    def scannerParameters(self, xml: str):
        super().scannerParameters(xml)
        open('scanner.xml', 'w').write(xml)
        print("ScannerParameters received.")


if __name__ == '__main__':
    app = MarketScanner()
    start(app, ACCOUNT_NAME, ACCOUNT_TYPE, SOFTWARE, CLIENT_ID)
    time.sleep(1)
    app.reqScannerParameters()
    time.sleep(3)
    disconnect(app)
