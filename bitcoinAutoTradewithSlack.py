import time
import pyupbit
import datetime
import requests
import schedule
import time

k = 0.5

# 매일 9시에 k값 구함


def get_ror():
    global k
    max_ror = 0
    for _k in np.arange(0.1, 1.0, 0.1):
        df = pyupbit.get_ohlcv("KRW-BTC", count=7)
        df['range'] = (df['high'] - df['low']) * _k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'],
                             1)

        ror = df['ror'].cumprod()[-2]
        if max_ror <= ror:
            max_ror = ror
            k = _k


schedule.every().day.at("09:00").do(get_ror)


access = "oKn7muzVmQGhOAYxjIPuHJsxD54z83QkDnVk5egl"
secret = "6dyRC8BGCy8HTt1n1bTLnIhiYvyEAfXxdXMIw20g"
tokenA = "xox"
tokenB = "b-1998820317235-201122"
tokenC = "5191057-iS7ec80KFH88T"
tokenD = "OGviPsZUEf4"
myToken = tokenA + tokenB + tokenC + tokenD


def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer "+token},
                             data={"channel": channel, "text": text}
                             )


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + \
        (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15


def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken, "#alarm", "autotrade start")
balances = upbit.get_balances()
print(balances)


while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", k)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    post_message(myToken, "#alarm",
                                 "BTC buy : " + str(buy_result))
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                post_message(myToken, "#alarm",
                             "BTC buy : " + str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken, "#alarm", e)
        time.sleep(1)
