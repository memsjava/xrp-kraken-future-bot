import requests
import time
import numpy
import requests
import numpy as np
import pandas as pd
import talib
from talib.abstract import *
from talib import abstract
from talib import MA_Type
from pykrakenapi import KrakenAPI
import krakenex
import os
import itertools
from random import randint
import time             # for sleep
import sched
import time
from datetime import datetime
import calendar
import json


import proxyFuture as pf


class MyPoketra():

    def __init__(self):
        try:
            self.api = pf.Proxy()
        except Exception as e:
            print(e)
        self.pair = 'xrpusd'
        self.performance = 0.0012
        with open("config.json", "r") as jsonfile:
            data = json.load(jsonfile)
        self.min_leverage = data['leverage'][0]
        self.max_leverage = data['leverage'][1]

    def calculateMACD(self, itemDict, fast, slow, signal):
        NAME = abstract.Function('MACD')
        macd, macdsignal, macdhist = NAME(
            itemDict['close'], fastperiod=fast, slowperiod=slow, signalperiod=signal)

        return macd, macdsignal, macdhist

    def calculateATR(self, itemDict, periode):
        NAME = abstract.Function('ATR')
        output = NAME(itemDict['high'], itemDict['low'],
                      itemDict['close'], timeperiod=periode)

        return output

    def getItemDict(self, pair, interval):
        ts = calendar.timegm(time.gmtime())
        ts = ts - 5000*60
        url_ = 'https://futures.kraken.com/api/charts/v1/spot/pi_' + \
            pair+'/'+str(interval)+'m?from='+str(ts)
        r = requests.get(url_)
        candles = r.json()
        candles = candles["candles"]
        h, k, l, m, n = [], [], [], [], []
        for item in candles:
            h.append(item['open'])
            k.append(item['high'])
            l.append(item['low'])
            m.append(item['close'])
            n.append(item['volume'])
        itemDict = {
            'open': np.asarray(h, dtype=np.float),
            'high': np.asarray(k, dtype=np.float),
            'low': np.asarray(l, dtype=np.float),
            'close': np.asarray(m, dtype=np.float),
            'volume': np.asarray(n, dtype=np.float)
        }
        return itemDict

    def getAndCloseOrder(self, pair):
        anyOrders = self.api.getOpenOrders()
        for anyOrder in anyOrders:
            if anyOrder['symbol'] == 'pi_'+pair:
                iD = anyOrder['order_id']
                print("cancel the current order")
                os.system(
                    'python krakenfuturesapi_original.py cancelorder order_id='+iD)

    def run(self):
        res = None
        res_ = None

        pair = self.pair
        pnlValue = self.api.getPNL(pair)

        now = datetime.utcnow()
        hour = now.hour
        variableBase = 5    # amount per trade base
        # stop loss percentage
        stop_loss = 20

        if hour > 0 and hour < 19:
            levier = self.max_leverage         # max leverage
            numberOfTrade = 5   # numnber of trade
        else:
            levier = self.min_leverage
            numberOfTrade = 6   # numnber of trade

        compteValue = int(self.api.getAccount(pair))
        a = round(compteValue/numberOfTrade)
        # amount per trade
        variable = variableBase if a < 5 else a
        anyPosition = self.api.getOpenPositions(pair)
        # get mark price
        price, fundingRate = self.getPriceAndFundingRate(
            pair, 'markPrice')
        # get candles 5 minute timeframe
        itemDict = self.getItemDict(pair, 5)

        if anyPosition:
            # calculate pips to close the order
            atr5 = self.calculateATR(itemDict, 5)
            self.performance = max(0.0012, float(
                atr5[-3]), float(atr5[-2]), float(atr5[-1]))
            self.performance = self.performance * max(1, int(5 / levier))

            if anyPosition[0]['side'] == 'short':
                res = 'sell'
                if float(anyPosition[0]['price']) - self.performance > price:
                    res_ = "close"

                if anyPosition[0]['size'] > compteValue*levier/3 or float(anyPosition[0]['price']) > price:
                    res = None

                if pnlValue < - compteValue * 2 / 100 and anyPosition[0]['size'] < compteValue*levier*2/3 and float(anyPosition[0]['price']) + self.performance < price and not res:
                    res = 'sell'

                if pnlValue < - compteValue * 4 / 100 and anyPosition[0]['size'] < compteValue*levier*2.2/3 and float(anyPosition[0]['price']) + self.performance < price and not res:
                    res = 'sell'

                if pnlValue < - compteValue * 8 / 100 and anyPosition[0]['size'] < compteValue*levier*2.4/3 and float(anyPosition[0]['price']) + self.performance < price and not res:
                    res = 'sell'

                if pnlValue < - compteValue * 16 / 100 and anyPosition[0]['size'] < compteValue*levier*2.6/3 and float(anyPosition[0]['price']) + self.performance < price and not res:
                    res = 'sell'

                if pnlValue < - compteValue * 32 / 100 and anyPosition[0]['size'] < compteValue*levier*2.8/3 and float(anyPosition[0]['price']) + self.performance < price and not res:
                    res = 'sell'

                if pnlValue < - compteValue * 64 / 100 and anyPosition[0]['size'] < compteValue*levier*3/3 and float(anyPosition[0]['price']) + self.performance < price and not res:
                    res = 'sell'

            else:
                res = 'buy'
                if float(anyPosition[0]['price']) + self.performance < price:
                    res_ = "close"

                if anyPosition[0]['size'] > compteValue*levier/3 or float(anyPosition[0]['price']) < price:
                    res = None

                if pnlValue < - compteValue * 2 / 100 and anyPosition[0]['size'] < compteValue*levier*2/3 and float(anyPosition[0]['price']) - self.performance > price and not res:
                    res = 'buy'

                if pnlValue < - compteValue * 4 / 100 and anyPosition[0]['size'] < compteValue*levier*2.2/3 and float(anyPosition[0]['price']) - self.performance > price and not res:
                    res = 'buy'

                if pnlValue < - compteValue * 8 / 100 and anyPosition[0]['size'] < compteValue*levier*2.4/3 and float(anyPosition[0]['price']) - self.performance > price and not res:
                    res = 'buy'

                if pnlValue < - compteValue * 16 / 100 and anyPosition[0]['size'] < compteValue*levier*2.6/3 and float(anyPosition[0]['price']) - self.performance > price and not res:
                    res = 'buy'

                if pnlValue < - compteValue * 32 / 100 and anyPosition[0]['size'] < compteValue*levier*2.8/3 and float(anyPosition[0]['price']) - self.performance > price and not res:
                    res = 'buy'

                if pnlValue < - compteValue * 64 / 100 and anyPosition[0]['size'] < compteValue*levier*3/3 and float(anyPosition[0]['price']) - self.performance > price and not res:
                    res = 'buy'

            # stop loss 20%
            if pnlValue < - compteValue * stop_loss / 100:
                res_ = "close"

            # attempt for propable liquidation
            if anyPosition[0]['size'] < compteValue*levier and not res:
                res = 'degany'

        else:
            # Trend
            macd1, macdsignal1, macdhist1 = self.calculateMACD(
                itemDict, 5, 400, 9)
            macd, macdsignal, macdhist = self.calculateMACD(
                itemDict, 8, 16, 9)

            # crossOver
            if macd[-2] < macdsignal[-2] and macd[-1] > macdsignal[-1]:
                self.getAndCloseOrder(pair)
                if macd1[-1] > 0:
                    res = 'buy'
            if macd[-2] > macdsignal[-2] and macd[-1] < macdsignal[-1]:
                self.getAndCloseOrder(pair)
                if macd1[-1] < 0:
                    res = 'sell'

        if res == 'sell':
            price = (itemDict['high'][-1] - itemDict['close']
                     [-1])/3*2 + itemDict['close'][-1]
            price = round(price, 4)
            self.sellShort(pair, price, variable)

        if res == 'buy':
            price = (itemDict['close'][-1] - itemDict['low']
                     [-1])/3*2 + itemDict['low'][-1]
            price = round(price, 4)
            self.buyLong(pair, price, variable)

        if res == 'degany':
            if anyPosition[0]['side'] == 'short':
                price = price + 0.0075
                variable = compteValue * levier / 2
                self.sellShort(pair, price, variable)
            else:
                price = price - 0.0075
                variable = compteValue * levier / 2
                self.buyLong(pair, price, variable)

        if res_ == 'close':
            if anyPosition[0]['side'] == 'short':
                self.buyLong(pair, price, anyPosition[0]['size'])
            else:
                self.sellShort(pair, price, anyPosition[0]['size'])
        if res == 'fire':
            if anyPosition[0]['side'] == 'short':
                self.buyLong(pair, price, variable)
            else:
                self.sellShort(pair, price, variable)

        print("it's now : %s h, Expected perf: %s,  Action to do now: %s" %
              (hour, self.performance, res))

    def getPriceAndFundingRate(self, pair, side):
        pair = "pi_"+pair
        r = requests.get(
            "https://futures.kraken.com/derivatives/api/v3/tickers")
        r = (r.json())
        tickers = r['tickers']
        index = next((index for (index, d) in enumerate(
            tickers) if d["symbol"] == pair), None)
        ticker = tickers[index]
        prix = ticker[side]
        funding = ticker["fundingRatePrediction"]
        return float(prix), funding

    def buyLong(self, pair, price, qtty):
        qtty = int(qtty)
        self.getAndCloseOrder(pair)
        symbol = 'pi_'+pair
        os.system('python krakenfuturesapi_original.py  sendorder orderType=lmt symbol=' +
                  symbol+' side=buy size='+str(qtty)+' limitPrice='+str(price))

    def sellShort(self, pair, price, qtty):
        qtty = int(qtty)
        self.getAndCloseOrder(pair)
        symbol = 'pi_'+pair
        os.system('python krakenfuturesapi_original.py  sendorder orderType=lmt symbol=' +
                  symbol+' side=sell size='+str(qtty)+' limitPrice='+str(price))


q = MyPoketra()
while (True):
    try:
        print("---------")
        q.run()
        print("---------")
        time.sleep(120)
    except Exception as e:
        print(e)
        time.sleep(15)
        pass
