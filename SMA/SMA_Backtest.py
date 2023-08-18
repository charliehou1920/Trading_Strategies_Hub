import numpy as np
import yfinance as yf 
import pandas as pd
from scipy.optimize import brute

class SMABacktester(object):
    def __init__(self,symbol,SMA1,SMA2,start,end):
        self.symbol = symbol
        self.SMA1 = SMA1
        self.SMA2 = SMA2
        self.start = start
        self.end = end
        self.results = None
        self.get_data()

    def get_data(self):
        raw = yf.download(self.symbol, start = self.start, end = self.end)
        df = raw[['Close']]
        df["return"] = np.log(df / df.shift(1))
        df['SMA1'] = df["Close"].rolling(self.SMA1).mean()
        df['SMA2'] = df["Close"].rolling(self.SMA2).mean()
        self.data = df

    def set_parameters(self, SMA1=None, SMA2=None):
        '''
          Updates SMA parameters and resp. time series.
        '''
        if SMA1 is not None:
            self.SMA1 = SMA1
            self.data['SMA1'] = self.data['Close'].rolling(self.SMA1).mean()
        if SMA2 is not None:
            self.SMA2 = SMA2
            self.data['SMA2'] = self.data['Close'].rolling(self.SMA2).mean()

    def run_strategy(self):
        '''
          Backtests the trading strategy.
        '''
        data = self.data.copy().dropna()
        


