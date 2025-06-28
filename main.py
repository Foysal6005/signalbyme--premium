import requests
import pandas as pd
import ta
from telegram import Bot
import time

# ✅ Bot Token & Chat ID
bot = Bot(token='7943729235:AAEj1TbkVxSo0Fd3q12H4i0a3AKA9bvpSRE')
chat_id = '6430123426'

# ✅ API Endpoint & Key (TwelveData)
api_key = '5cd3403cd8994ae18204b9579adec1cf'
symbol = 'EUR/USD'
interval = '1min'

def get_signal():
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={api_key}&outputsize=100&format=JSON"
    response = requests.get(url).json()
    
    if 'values' not in response:
        return None

    df = pd.DataFrame(response['values'])
    df = df.iloc[::-1]  # Reverse for proper order
    df['close'] = df['close'].astype(float)

    # Indicators Calculation
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['ema'] = ta.trend.EMAIndicator(df['close'], window=14).ema_indicator()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()

    # ✅ Premium Safe Signal Condition
    if (df['rsi'].iloc[-1] < 30) and (df['close'].iloc[-1] < df['bb_lower'].iloc[-1]) and (df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]) and (df['close'].iloc[-1] > df['ema'].iloc[-1]):
        return "✅ BUY SIGNAL | EUR/USD | 1M | PREMIUM SAFE"
    elif (df['rsi'].iloc[-1] > 70) and (df['close'].iloc[-1] > df['bb_upper'].iloc[-1]) and (df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]) and (df['close'].iloc[-1] < df['ema'].iloc[-1]):
        return "✅ SELL SIGNAL | EUR/USD | 1M | PREMIUM SAFE"
    else:
        return None

# ✅ Bot Loop
while True:
    try:
        signal = get_signal()
        if signal:
            bot.send_message(chat_id=chat_id, text=signal)
            print("Signal sent ✅")
        else:
            print("No valid signal ❌")
    except Exception as e:
        print("Error:", e)

    time.sleep(300)  # 5 minutes delay