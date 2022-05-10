from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time
import sys
from ibapi.client import logger, socket
# from _Inputs import start_info
# TESTING PARAMS
import _vars as v


class App(EClient, EWrapper):
    """
    App Handler Functions
    """
    def __init__(self):
        EClient.__init__(self, self)
        EWrapper.__init__(self)
        # ERROR
        self.error_code = 0

    def recvMsg(self):
        if not self.isConnected():
            logger.debug("recvMsg attempted while not connected, releasing lock")
            return b""
        try:
            buf = self._recvAllMsg()
            # receiving 0 bytes outside a timeout means the connection is either
            # closed or broken
            if len(buf) == 0:
                logger.debug("socket either closed or broken, disconnecting")
                self.disconnect()
        except socket.timeout:
            logger.debug("socket timeout from recvMsg %s", sys.exc_info())
            buf = b""
        except socket.error:
            logger.debug("socket broken, disconnecting")
            self.disconnect()
            buf = b""
        else:
            pass

    def error(self, reqId, errorCode, errorString):
        # ELIMINATING THE FOLLOWING ERROR CODES FROM THE CALLS
        eliminate_codes = [2104, 2106, 2158, -1, 2100, 2137,399,2168,2169]

        if errorCode not in eliminate_codes:
            print("<< Code:", errorCode, errorString, ">>")
        self.error_code = errorCode


def socket_connection(appObj):
    appObj.run()


def start(app, accName= "Meesam", accType= "Paper", software = 'TWS',HOST='127.0.0.1',PORT=7497, clientId=0):
    # app_info = start_info(accName, accType, software)
    # HOST = app_info[0]
    # PORT = app_info[1]
    if app.isConnected():
        print("Already Connected")
    else:
        app.connect(HOST, PORT, clientId)
        thread = threading.Thread(target = socket_connection, daemon = True, args=(app,))
        thread.start()
        time.sleep(0.3)


def disconnect(app):
    app.disconnect()


if __name__ == "__main__":
    app = App()
    print("Initialized...")
    start(app,v.ACCOUNT_NAME,v.ACCOUNT_TYPE,v.SOFTWARE,v.HOST,v.PORT,clientId=v.CLIENT_ID)
    print("Start...")
    input("Press Enter to Disconnect....")
    disconnect(app)
    print("Program Exited...")
