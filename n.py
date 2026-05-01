
import time
import requests
import hmac
import urllib.parse
from hashlib import sha256

APIURL = "https://open-api-vst.bingx.com"
APIKEY = "SnOOQDiwELC2WIvhzNU8zFrbZ2ul6OrUPQ9s9MGVHv7vOCi6JJb80F0mVsBkxV7NlyoQQ0arb7C1fP6j3Q"
SECRETKEY = "RhcxYAQKO9lnMrcg8ZM85ehPEY3sUelrp6oQDYhiEE6dgoclrk4gQNQnqao0iJtyj2fBpn7KaDBaxydxjY2Q"

def parseParam(paramsMap):
    
    sortedKeys = sorted(paramsMap)
    paramsList = []
    urlParamsList = []
    for x in sortedKeys:
        value = paramsMap[x]
        paramsList.append("%s=%s" % (x, value))
    timestamp = str(int(time.time() * 1000))
    paramsStr = "&".join(paramsList)
    if paramsStr != "": 
        paramsStr = paramsStr + "&timestamp=" + timestamp
    else:
        paramsStr = "timestamp=" + timestamp
    contains = '[' in paramsStr or '{' in paramsStr
    for x in sortedKeys:
        value = paramsMap[x]
        if contains:
            encodedValue = urllib.parse.quote(str(value), safe='')
            urlParamsList.append("%s=%s" % (x, encodedValue))
        else:
            urlParamsList.append("%s=%s" % (x, value))
    urlParamsStr = "&".join(urlParamsList)
    if urlParamsStr != "": 
        urlParamsStr = urlParamsStr + "&timestamp=" + timestamp
    else:
        urlParamsStr = "timestamp=" + timestamp
    return paramsStr, urlParamsStr

def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    return signature


def send_request(method, path, paramsStr, urlParamsStr, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlParamsStr, get_sign(SECRETKEY, paramsStr))
    print(url)
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload)
    return response.json()  # Преобразует JSON в словарь


def demo():
    payload = {}
    path = '/openApi/swap/v3/quote/klines'
    method = "GET"
    paramsMap = {'symbol': 'BTC-USDT', 'timestamp': int(time.time() * 1000), 'interval': '1m', 'limit': '100'}
    paramsStr, urlParamsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, urlParamsStr, payload)

def place_order(symbol = 'BTC-USDT', side = 'long', tp = 0, sl = 0, qty = 0):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    paramsMap = { 
      "symbol": symbol,
      "side": side,
      "positionSide": "BOTH",
      "type": "MARKET",
      "quantity": qty,
      'timestamp': int(time.time() * 1000)
    }
    paramsStr, urlParamsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, urlParamsStr, payload)




def place_sl(symbol = 'BTC-USDT', side = 'long', sl = 0, qty = 0):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    if side == 'long':
        side = 'BUY'
    else:
        side = 'SELL'
        
    paramsMap = { 
     "type": "STOP_MARKET",
      "stopPrice": sl,
      "symbol": symbol,
      "side": side,
      "quantity": qty,
      "positionSide": "BOTH",
      "clientOrderID": "",
      "recvWindow": 5000,
      "timeInForce": "GTC",
      "timestamp": int(time.time() * 1000)
    }
    paramsStr, urlParamsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, urlParamsStr, payload)

def place_tp(symbol = 'BTC-USDT', side = 'long', tp = 0, qty = 0):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    if side == 'long':
        side = 'BUY'
    else:
        side = 'SELL'
    paramsMap = { 
     "type": "TAKE_PROFIT_MARKET",
      "stopPrice": tp,
      "symbol": symbol,
      "side": side,
      "quantity": qty,
      "positionSide": "BOTH",
      "clientOrderID": "",
      "recvWindow": 5000,
      "timeInForce": "GTC",
      "timestamp": int(time.time() * 1000)
    }
    paramsStr, urlParamsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, urlParamsStr, payload)


def place_order(symbol = 'BTC-USDT', side = 'long', tp = 0, sl = 0, qty = 0):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    if side == 'long':
        side = 'BUY'
    else:
        side = 'SELL'
    paramsMap = { 
      "symbol": symbol,
      "side": side,
      "positionSide": "BOTH",
      "type": "MARKET",
      "quantity": qty,
      'timestamp': int(time.time() * 1000)
    }
    paramsStr, urlParamsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, urlParamsStr, payload)



import pandas as pd
import numpy as np


# Альтернативная версия с более точным расчетом по методу Уайлдера
def rsi_wilder(df, period=5):
    """
    Расчет RSI с использованием экспоненциального сглаживания (метод Уайлдера)
    
    Параметры:
    df: DataFrame с колонкой 'close'
    period: период расчета RSI
    
    Возвращает:
    DataFrame с добавленной колонкой 'rsi'
    """
    if isinstance(df, list):
        df = pd.DataFrame(df)
    
    if 'time' in df.columns:
        df = df.sort_values('time', ascending=True)
        df = df.reset_index(drop=True)
    
    df['close'] = pd.to_numeric(df['close'])
    
    # Шаг 1: Изменения цены
    delta = df['close'].diff()
    
    # Шаг 2: Разделяем на gains и losses
    gains = delta.copy()
    losses = delta.copy()
    
    gains[gains < 0] = 0
    losses[losses > 0] = 0
    losses = losses.abs()

    
    # Шаг 3: Создаем массивы для средних значений
    avg_gain = pd.Series(np.nan, index=df.index)
    avg_loss = pd.Series(np.nan, index=df.index)
    
    # Шаг 4: Первое среднее - простое среднее первых 'period' значений
    # (начинаем с индекса period, так как до этого недостаточно данных)
    if len(gains) > period:
        avg_gain.iloc[period] = gains.iloc[1:period+1].mean()  # gains[1]..gains[period]
        avg_loss.iloc[period] = losses.iloc[1:period+1].mean()  # losses[1]..losses[period]
        
        # Шаг 5: Экспоненциальное сглаживание для последующих значений
        for i in range(period + 1, len(gains)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gains.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + losses.iloc[i]) / period
    
    # Шаг 6: Расчет RS и RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Обработка случая, когда avg_loss = 0 (цена только растет)
    rsi[avg_loss == 0] = 100
    
    # Обработка случая, когда avg_gain = 0 (цена только падает)
    rsi[avg_gain == 0] = 0
    
    df['rsi'] = rsi
    
    return df



def get_klines():
    responce = demo()
    data = (responce['data'])   
    return data 

def update_rsi(current_data, period=5):
    df = rsi_wilder(current_data, period)
    return df['rsi'].iloc[-2]

from datetime import datetime

qty = 0.1
stop_percent = 0.002
take_percent = 0.002
def enter_short(mark_price):
    stop = mark_price * (1 + stop_percent)
    take = mark_price * (1 - stop_percent)
    r1 = place_order(symbol = 'BTC-USDT', side = 'short', qty = qty)
    r2 = place_sl(symbol = 'BTC-USDT', side = 'short', sl = stop, qty = qty)
    r3 = place_tp(symbol = 'BTC-USDT', side = 'short', tp = take, qty = qty)
    print(r1,r2,r3)
    
def enter_long(mark_price):
    stop = mark_price * (1 - stop_percent)
    take = mark_price * (1 + stop_percent)
    r1 = place_order(symbol = 'BTC-USDT', side = 'long', qty = qty)
    r2 = place_sl(symbol = 'BTC-USDT', side = 'long', sl = stop, qty = qty)
    r3 = place_tp(symbol = 'BTC-USDT', side = 'long', tp = take, qty = qty)
    print(r1,r2,r3)
    
while True:
    now = datetime.now()
    seconds = now.second
    if seconds == 1:
        current_data = get_klines()
        rsi = update_rsi(current_data)
        price = float(current_data[0].get('open'))
        
        print('current rsi:', rsi)
        if rsi > 70:
            enter_short(price)
        if rsi < 30:
            enter_long(price)
        time.sleep(1)
    
   


    
    