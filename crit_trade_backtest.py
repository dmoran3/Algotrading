from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

#three_month_list = []
#fill_list = False
#max_remaining_days = 1
#day = 0
# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close
        self.three_month_list = []
        self.max_remaining_days = 1
        self.day = 0
        self.current_max = 0
        

        # To keep track of pending orders
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        if len(self.three_month_list) < 60:
            self.three_month_list.append(self.datahigh[0])
            self.current_max = max(self.three_month_list)
        #elif len(three_month_list) == 60 and fill_list = False: 
            #self.current_max = max(three_month_list)
            #fill_list = True
            #max_remaining_days = 59
            #three_month_list.pop(0)
            #threemonth_list.append(self.datahigh[0])
        else:
            self.max_remaining_days -= 1
            self.three_month_list.pop(0)
            self.three_month_list.append(self.datahigh[0])
            
            if self.max_remaining_days == 0 :
                self.current_max = max(self.three_month_list)
                self.max_remaining_days = 60
                print('day: ', self.day)
                print('New max (run out): ', self.current_max)

            if self.datahigh[0] > self.current_max:
                self.current_max = self.datahigh[0]
                self.max_remaining_days = 60
                high_break = True

                print('day: ', self.day)
                print('New max (higher value): ', self.current_max)
        print('current 3-month max: ', self.current_max)
        self.day += 1

        #self.log('Close, %.2f' % self.dataclose[0])
        #print(self.dataopen[0], self.datahigh[0], self.datalow[0], self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if high_break = True 
            

            """if self.dataclose[0] < self.dataclose[-1]:
                    # current close less than previous close

                    if self.dataclose[-1] < self.dataclose[-2]:
                        # previous close less than the previous close

                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()"""


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    #modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    #datapath = os.path.join(modpath, '../../datas/orcl-1995-2014.txt')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname='AAPL.csv',
        # Do not pass values before this date
        fromdate=datetime.datetime(2016, 1, 20),
        # Do not pass values before this date
        todate=datetime.datetime(2020, 1, 20),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())