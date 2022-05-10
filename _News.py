# Local Imports
from _Connection import start, disconnect
from _Contract import InstrumentContract, stk_contract

# TESTING PARAMS
import _vars as v

# Imports
import time
from datetime import datetime
import pandas as pd
import os
from tabulate import tabulate

pd.set_option('display.max_rows',999)
pd.set_option('max_columns',None)
pd.set_option("expand_frame_repr", False)
pd.set_option('display.max_colwidth', None)


class News(InstrumentContract):
    def __init__(self):
        InstrumentContract.__init__(self)
        # LIST OF ALL NEWS PROVIDERS
        self.news_providers = {}
        # TICKER NEWS DF (lastest)
        self.tkr_news_df = pd.DataFrame(
            columns = ['tickerId', 'TimeStamp', 'providerCode', 'Headline', 'ArticleId', 'ExtraData'])
        # NEWS ATRICLE (BODY)
        self.article_body = ""
        self.article_type = ""
        # HISTORICAL NEWS DF
        self.historical_news_df = pd.DataFrame(
            columns = ['requestId', 'TimeStamp', 'providerCode', 'Headlines', 'ArticleId'])

    # NEWS PROVIDERS LIST
    def newsProviders(self, newsProviders):
        # print("NewsProviders: ")
        for provider in newsProviders:
            # print("NewsProvider.", provider)
            self.news_providers[provider.code] = provider.name
        # print("*" * 50)

    def tickNews(self, tickerId: int, timeStamp: int, providerCode: str, articleId: str, headline: str, extraData: str):
        super().tickNews(tickerId, timeStamp, providerCode, articleId, headline, extraData)
        # FORMAT DATETIME
        time_stamp = int(str(timeStamp)[:-3])
        timeStamp = datetime.fromtimestamp(time_stamp)

        # Add news as a new row to the tkr_news_df
        _news = [tickerId, timeStamp, providerCode, headline, articleId, extraData]
        len_df = len(self.tkr_news_df)
        self.tkr_news_df.loc[len_df] = _news
        self.tkr_news_df.sort_values('TimeStamp', ignore_index = True, inplace= True)

        # PRINT STATEMENT FOR NEWS HEADLINES
        # _tick_news_statement = f"""TimeStamp: {timeStamp} -- {providerCode}\nHeadline: {headline}\nExtraData: {extraData}"""
        # print(_tick_news_statement)

    def newsArticle(self, requestId: int, articleType: int, articleText: str):
        print(f"Req:{requestId} ArticleType:{articleType}\n{articleText}")
        self.article_body = articleText
        self.article_type = articleType


def tkrLatestNews(ticker:list,account="Meesam",accountType="Paper",clientId=41):
    # INITIALIZE AND START
    app = News()
    start(app, account,accountType, clientId=clientId)
    ### NEWS PROVIDER
    app.reqNewsProviders()
    time.sleep(0.5)
    # print(app.news_providers)
    providers = list(app.news_providers.keys())
    print("*" * 100)
    i = 1000
    contract = stk_contract(ticker)
    ### TICKER NEWS
    for i, provider in enumerate(providers):
        i += 1
        # print(f"PROVIDER:{provider}")
        # print("*" * 100)
        app.reqMktData(i, stk_contract(ticker), f"mdoff,292:{provider}", False, False, [])
        time.sleep(2)
        app.cancelMktData(i)  # print("*" * 100)
    # DISCONNECT
    disconnect(app)

    # print(app.tkr_news_df)
    print(tabulate(app.tkr_news_df, showindex = False, headers = app.tkr_news_df.columns))
    # SAVE NEWS
    _news_archive_path = os.path.join(os.getenv("STOCK_DATA_PATH"),'News_ib')
    ticker_news_path = os.path.join(_news_archive_path,f'{ticker}.csv')
    if not os.path.exists(_news_archive_path):
        os.mkdir(_news_archive_path)
        app.tkr_news_df.to_csv(ticker_news_path, sep = "|")
    else:
        if os.path.exists(ticker_news_path):
            main_df = pd.read_csv(ticker_news_path, sep = '|', index_col = 0)
            main_df = main_df.append(app.tkr_news_df)
            main_df = main_df[~main_df['ArticleId'].duplicated(keep = 'last')]
        else:
            main_df = app.tkr_news_df
        main_df.to_csv(ticker_news_path, sep = "|")
    input("Press Enter to Continue...")


if __name__ == '__main__':
    tickers = []
    ticker = (input("Enter a ticker: ") or "").upper()
    while ticker != "":
        tickers.append(ticker)
        ticker = (input("Enter a ticker: ") or "").upper()

    tkrLatestNews(tickers)
