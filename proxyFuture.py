import sys
import platform
import base64
import hashlib
import hmac
import urllib.request as urllib2
import json


class Proxy():

    def __init__(self):
        self.api_path = "/api/v3/"
        self.api_domain = "https://futures.kraken.com/derivatives"
        self.api_key = open("Futures_Public_Key").read().strip()
        self.api_secret = base64.b64decode(
            open("Futures_Private_Key").read().strip())

    def tickers(self):
        api_data = ""
        api_request = urllib2.Request(
            self.api_domain + self.api_path + "tickers?" + api_data)
        api_request.add_header("User-Agent", "Kraken Futures REST API")
        return self.getResult(api_request)

    def getInstruments(self):
        pass

    def getResult(self, api_request):
        try:
            api_reply = urllib2.urlopen(api_request).read().decode()
        except Exception as error:
            print("API call failed due to unexpected error (%s)" % error)
        if '"result":"success"' in api_reply:
            # print(api_reply)
            return (api_reply)
        else:
            print(api_reply)
            return (api_reply)

    def singleArgOperation(self, api_method):
        api_data = ""
        api_postdata = api_data.encode('utf-8')
        api_sha256 = hashlib.sha256(
            api_postdata + self.api_path.encode('utf-8') + api_method.encode('utf-8')).digest()
        api_hmacsha512 = hmac.new(self.api_secret, api_sha256, hashlib.sha512)
        api_request = urllib2.Request(
            self.api_domain + self.api_path + api_method + "?" + api_data)
        api_request.add_header("APIKey", self.api_key)
        api_request.add_header(
            "Authent", base64.b64encode(api_hmacsha512.digest()))
        api_request.add_header("User-Agent", "Kraken Futures REST API")
        return self.getResult(api_request)

    def multipleArgOperation(self, api_method, **kwargs):
        api_method = api_method
        api_data = ''
        for key, value in kwargs.items():
            api_data = api_data + "&" + str(key)+'=' + str(value)
        api_postdata = api_data.encode('utf-8')
        api_sha256 = hashlib.sha256(
            api_postdata + self.api_path.encode('utf-8') + api_method.encode('utf-8')).digest()
        api_hmacsha512 = hmac.new(self.api_secret, api_sha256, hashlib.sha512)
        api_request = urllib2.Request(
            self.api_domain + self.api_path + api_method, api_postdata)
        api_request.add_header("APIKey", self.api_key)
        api_request.add_header(
            "Authent", base64.b64encode(api_hmacsha512.digest()))
        api_request.add_header("User-Agent", "Kraken Futures REST API")
        return self.getResult(api_request)

    def getAccounts(self):
        accounts = self.singleArgOperation("accounts")
        return json.loads(accounts)

    def getPNL(self, pair):
        accounts = self.getAccounts()
        account = accounts['accounts']
        accPair = account['fi_'+pair]
        accPair = accPair['auxiliary']
        pnl = accPair['pnl']
        return pnl

    def getAccount(self, pair):
        a = self.getAccounts()
        return a['accounts']['fi_'+pair]['balances'][pair[:-3]]

    def getOpenPositions(self, pair):
        openpositions = self.singleArgOperation("openpositions")
        openpositions = json.loads(openpositions)
        # print ('open position',openpositions)
        openpositions = openpositions['openPositions']
        for position in openpositions:
            if 'pi_'+pair == position['symbol']:
                return [position]

    def getOpenOrders(self):
        openorders = self.singleArgOperation("openorders")
        openorders = json.loads(openorders)
        print('open order', openorders)
        return openorders['openOrders']
    # sendorder?orderType=lmt&symbol=pi_xbtusd&side=buy&size=10000&limitPrice=9400&reduceOnly=true

    def makeOrder(self, **kwargs):
        order = self.multipleArgOperation('sendorder', **kwargs)
        return json.loads(order)

    def closeOrder(self, **kwargs):
        pass
