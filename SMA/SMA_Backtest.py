import numpy as np
import yfinance as yf 
import pandas as pd
from scipy.optimize import brute

'''
In scipy.optimize, the brute function performs a brute-force search over a 
given parameter space to find the minimum of a function. 
It evaluates the function on a regular grid of points 
and returns the parameters that correspond to the minimum value. 
This can be useful when you don't have a good idea of 
where the minimum might be, but it can be 
computationally intensive for large parameter spaces.
'''

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
        data['position'] = np.where(data['SMA1']>data['SMA2'],1,-1)
        data['strategy'] = data['position'].shift(1) * data['return']
        data.dropna(inplace=True)
        data['creturns'] = data['return'].cumsum().apply(np.exp)
        data['cstrategy'] = data['strategy'].cumsum().apply(np.exp)
        self.results = data
        # gross performance of the strategy
        aperf = data['cstrategy'].iloc[-1]
        # out-/underperformance of strategy
        operf = aperf - data['creturns'].iloc[-1]
        return round(aperf, 2), round(operf, 2)
    
    def plot_results(self):
        ''' 
        Plots the cumulative performance of the trading strategy
        compared to the symbol.
        '''
        if self.results is None:
            print('No results to plot yet. Run a strategy.')

        title = '%s | SMA1=%d, SMA2=%d' % (self.symbol, self.SMA1, self.SMA2)

        self.results[['creturns', 'cstrategy']].plot(title=title, figsize=(10, 6))

    def update_and_run(self, SMA):
        ''' Updates SMA parameters and returns negative absolute performance
        (for minimazation algorithm).

        Parameters
        ==========
        SMA: tuple
            SMA parameter tuple
        '''
        self.set_parameters(int(SMA[0]), int(SMA[1]))
        return -self.run_strategy()[0]
    
    def optimize_parameters(self, SMA1_range, SMA2_range):
        ''' Finds global maximum given the SMA parameter ranges.

        Parameters
        ==========
        SMA1_range, SMA2_range: tuple
            tuples of the form (start, end, step size)
        '''
        opt = brute(self.update_and_run, (SMA1_range, SMA2_range), finish=None)
        return opt, -self.update_and_run(opt)
    

        


