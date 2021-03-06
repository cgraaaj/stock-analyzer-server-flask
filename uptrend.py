import sys
import time
import pandas as pd
import numpy as np
import pandas_datareader as web
import datetime as dt
import time
import pickle
from datetime import datetime
from pprint import pprint

sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
from nsetools.nse import Nse
from driver import Driver



class Uptrend:
    def __init__(self):
        self.nse = Nse()
        self.dri = Driver()
        self.res = []
        self.total = []
        self.volBased = []
        self.trackedStocks = set()

    def get_uptrend(self, stock, retry):
        # print(f"checking {stock}")
        self.total.append(stock)
        rnge = 4
        try:
            ticker_data = self.dri.get_ticker_data(
                ticker=stock, range=str(rnge) + "d", interval="1d"
            )
            ticker_data["uptrend"] = (
                ticker_data["Close"] > ticker_data["Close"].shift(1)
            ) & (ticker_data["Close"] > ticker_data["Open"])
            self.check_data(stock, ticker_data, rnge, retry)
            if (
                ticker_data["uptrend"].values.sum() == ticker_data.shape[0] - 1
                and ticker_data.shape[0] == rnge
            ):
                # print(ticker_data)
                print(stock)
                self.res.append(stock)
                if ticker_data["Volume"].iloc[-1] > (
                    ticker_data.iloc[:-1, -2].mean(axis=0)
                ):
                    self.volBased.append(
                        {"name": stock, "volume": ticker_data["Volume"].iloc[-1]}
                    )
        except Exception as e:
            print(e)

    def get_flat(self, stock):
        rnge = 15
        start = dt.datetime.now() - dt.timedelta(days=rnge)
        end = dt.datetime.now()
        ticker_data = web.DataReader(stock, "yahoo", start, end)
        ticker_data["isFlat"] = (
            (ticker_data["Close"] <= ticker_data.iloc[0]["Close"])
            & (
                ticker_data["Close"]
                > (ticker_data.iloc[0]["Close"] - (ticker_data.iloc[0]["Close"] * 0.02))
            )
            & (
                ticker_data["Close"]
                < (ticker_data.iloc[0]["Close"] + (ticker_data.iloc[0]["Close"] * 0.02))
            )
        )
        if ticker_data["isFlat"].values.sum() >= ticker_data.shape[0] * 0.80:
            print(ticker_data)
            self.res.append(stock)

    def check_data(self, stock, ticker_data, rnge, retry):
        if ticker_data.shape[0] != rnge and retry < 2:
            retry += 1
            print(f"checking again {stock} {retry} time")
            print(ticker_data)
            print(f'data length is {len(set(self.total))}')
            time.sleep(180)
            self.get_uptrend(stock, retry)

    def nifty_stocks(self):
        sectors = pd.read_csv(
            "/home/pudge/Trading/python_trading/Src/nsetools/sectorKeywords.csv"
        )
        # sectors = ["Nifty Smallcap 250"]
        # for sec in sectors["Sector"].head(17):
        for sec in sectors["Sector"]:
            print(sec)
            stocks_of_sector = pd.DataFrame(self.nse.get_stocks_of_sector(sector=sec))
            stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(
                lambda x: x + ".NS"
            )
            # with concurrent.futures.ProcessPoolExecutor() as executor:
            #     executor.map(get_uptrend, stocks_of_sector["symbol"])
            for stock in stocks_of_sector["symbol"]:
                self.get_uptrend(stock, retry=0)
                self.trackedStocks.add(stock.split(".")[0])
                # get_flat(stock)
        result = list(set(self.res))
        volumeBased = [dict(t) for t in set(tuple(d.items()) for d in self.volBased)]
        # sory by volume decend
        volumeBased = sorted(
            volumeBased, key=lambda stock: stock["volume"], reverse=True
        )
        # print("volume based")
        self.send(result, volumeBased)

    def otherthan_nifty_stocks(self,untracked=True):
        if untracked:
            all_stocks_pd = pd.read_csv(
                "/home/pudge/Trading/python_trading/Src/nsetools/allStocks.csv"
            )
            all_stocks_pd = all_stocks_pd[
                all_stocks_pd.iloc[:, 3].apply(
                    lambda x: datetime.strptime(x, "%d-%b-%Y")
                    < datetime.today() - dt.timedelta(days=14)
                )
            ]
            # all_stocks_pd['SYMBOL'].where(all_stocks_pd['SYMBOL'] == 'GRINFRA').dropna()
            all_stocks = [stock for stock in all_stocks_pd["SYMBOL"]]
            untracked_stocks = set(all_stocks) - self.trackedStocks
            # serialize to a file
            with open("/home/pudge/Trading/python_trading/Src/utils/pickle_data/untracked_stocks", "wb") as fp:
                pickle.dump(untracked_stocks, fp)
        else:
            with open ('/home/pudge/Trading/python_trading/Src/utils/pickle_data/untracked_medium_cap_stocks', 'rb') as fp:
                untracked_stocks = pickle.load(fp)
        print(len(untracked_stocks))
        for stock in [stock + ".NS" for stock in untracked_stocks]:
            self.get_uptrend(stock, retry=0)
            # get_flat(stock)
        result = list(set(self.res))
        # pprint(f"final result {res}")
        # removing duplicate dicts
        volumeBased = [dict(t) for t in set(tuple(d.items()) for d in self.volBased)]
        # sort by volume decend
        volumeBased = sorted(
            volumeBased, key=lambda stock: stock["volume"], reverse=True
        )
        # print("volume based")
        self.send(result, volumeBased)

niftyUptrend = Uptrend()
niftyUptrend.nifty_stocks()
niftyUptrend = Uptrend()
niftyUptrend.otherthan_nifty_stocks(untracked=False)
# niftyUptrend.otherthan_nifty_stocks()
# niftyUptrend.get_uptrend("EMAMIPAP.NS")
