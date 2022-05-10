# IMPORTING TEMPLATES
from _Connection import App, start, disconnect
from _Contract import stk_contract

# TESTING PARAMS
import _vars as v

# BUILTIN IMPORTS
import time
import pandas as pd
import os
from datetime import datetime, timedelta
import sys
from tqdm import tqdm


class OHLCData(App):
    """
    App Handler Functions
    """
    def __init__(self):
        App.__init__(self)
        # TICKER DATAFRAME DICT
        self.data = {}
        # self.main_df = pd.DataFrame(columns = ["Date", "Open", "High", "Low", "Close", "Volume"])

    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = [
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume}]
        else:
            self.data[reqId].append(
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume})
        # len_df = len(self.main_df)
        # self.main_df.loc[len_df] = [bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume]

    def historicalDataEnd(self, reqId:int, start:str, end:str):
        print(f"{reqId}: {start} >> {end}")

    


    def DataReader(self, req_id, ticker:str, endTime:str= "", duration:str= '1 D', interval= '1 min'):
        # REQUEST HISTORICAL DATA
        self.reqHistoricalData(
            reqId = req_id,
            contract = stk_contract(ticker),
            endDateTime = endTime,
            durationStr = duration,
            barSizeSetting = interval,
            whatToShow = 'TRADES',
            useRTH = 0,
            formatDate = 1,
            keepUpToDate = 1,
            chartOptions = []
            )
        time.sleep(1)
        if self.error_code in [321, 162, 504]:
            self.disconnect()
            sys.exit()
        # extract and store historical data in dataframe
        df_data = pd.DataFrame(columns = ["Date", "Open", "High", "Low", "Close", "Volume"])

        try:
            df_data = pd.DataFrame(self.data[req_id])
            time.sleep(1)
            df_data.set_index("Date", inplace=True)
            df_data.index = pd.to_datetime(df_data.index)

            if req_id % 100 == 0:
                print(f"LastEntry TimeStamp: {df_data.iloc[-1].name}")
        except:
            print(f"Data Retrieving ERROR for {ticker}")
            disconnect(app)
            sys.exit()

        time.sleep(1)

        return df_data


def datetime_range(_start, end, delta):
    current = _start
    while current <= end:
        if (9 < current.hour <= 16) and (current.weekday() in [0, 1, 2, 3, 4]):
            yield current
        current += delta


if __name__ == '__main__':
    app = OHLCData()
    start(app,v.ACCOUNT_NAME,v.ACCOUNT_TYPE,v.SOFTWARE,clientId=v.CLIENT_ID)

    # GET LIST OF TICKERS
    tickers = v.tickers
    # *********************
    total_wait = len(tickers)*10
    total_wait = 12
    # *********************

    # TIME INTERVAL AND DURATION
    duration = v.duration
    interval = v.interval
    # ****** 1 request per 10 seconds ******
    delta = v.delta
    UNIT = v.unit

    # CONVERT DELTA TO UNITS
    if UNIT == 'H':
        delta *= 3600

    TOTAL_DAYS_BACK = 1

    for ticker in tickers:
        print(f"Downloading: {ticker}")
        
        source_path = os.path.join(os.getenv("STOCK_DATA_PATH"),'OHLC_ib',interval,f'{ticker}.csv')
        # Create New Folder
        fldr_path = os.path.dirname(source_path)
        if not os.path.exists(fldr_path):
            os.mkdir(fldr_path)
        file_name = source_path
        print(file_name)

        if os.path.exists(source_path):
            start_date = pd.read_csv(source_path, index_col = 0).iloc[-1].name
            _start = datetime.strptime(start_date, '%Y%m%d %H:%M:%S') + timedelta(seconds=delta)
            print(f"Starting Query: {_start}")
        else:
            _start = datetime.today() - timedelta(days = TOTAL_DAYS_BACK)
            _start = _start.replace(hour = 0, minute = 30, second = 0, microsecond = 0)
            print(f"Starting Query: {_start}")

        # INTERVALS FROM STARTDATE
        dts = [dt.strftime('%Y%m%d %H:%M:%S') for dt in datetime_range(_start, datetime.today(), timedelta(seconds=delta))]

        # # REQUESTING EACH QUERY
        req_id = 0
        for queryTime in tqdm(dts):
            if req_id % 100 == 0:
                print("QueryTime:",queryTime)
            # *********************
            _start_time = datetime.now()
            # *********************
            # changing data_dict to new_df
            new_df = app.DataReader(req_id, ticker, queryTime, duration, interval)
            time.sleep(2)
            # Save Data

            if os.path.exists(file_name):
                df = pd.read_csv(file_name, index_col = 0)
                df = df.append(new_df)
                df = df[~df.duplicated(keep = 'last')]
                df.sort_index(axis = 0, ascending = True, inplace=True)
            else:
                df = new_df
            df.to_csv(file_name)
            time.sleep(1)

            time_processed = (datetime.now() - _start_time).total_seconds()
            if time_processed <= total_wait:
                WAIT = total_wait-time_processed
                # print(f"Wait: {WAIT}")
                time.sleep(WAIT)
            req_id+=1

    disconnect(app)
