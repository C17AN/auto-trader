import time
import pyupbit
import datetime
import requests
import schedule
import numpy as np
import time

k = 0.5

# 매일 9시에 k값 구함


def check_alive():
    post_message(myToken, "#alarm", "봇 동작중")


def get_ror():
    global k
    max_ror = 0
    for _k in np.arange(0.1, 1.0, 0.1):
        df = pyupbit.get_ohlcv("KRW-BTC", interval="minute30", count=7)
        df['range'] = (df['high'] - df['low']) * _k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'],
                             1)

        ror = df['ror'].cumprod()[-2]
        if max_ror < ror:
            max_ror = ror
            k = _k
    post_message(myToken, "#alarm", "매수 목표가 : " +
                 str(get_target_price("KRW-BTC", k)))


# schedule.every().day.at("09:00").do(get_ror)
schedule.every().hour.do(get_ror)

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
    df = pyupbit.get_ohlcv(ticker, interval="minute3", count=2)
    target_price = df.iloc[0]['close'] + \
        (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_ma3min(ticker):
    """3분단위 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute3", count=3)
    ma3min = df['close'].rolling(3).mean().iloc[-1]
    return ma3min


def get_ma30min(ticker):
    """30분단위 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute30", count=5)
    ma30min = df['close'].rolling(3).mean().iloc[-1]
    return ma30min


def get_ma3(ticker):
    """3일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=3)
    ma3 = df['close'].rolling(3).mean().iloc[-1]
    return ma3


def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5


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
post_message(myToken, "#alarm", "매매 시작")
# 구매시 평단
# 무조건 바꿔줘야함
avg_buy = 62791899
get_ror()


while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", k)
            krw = get_balance("KRW")
            btc = get_balance("BTC")
            ma30min = get_ma30min("KRW-BTC")
            # 3일 이평선
            # ma3 = get_ma3("KRW-BTC")
            # # 5일 이평선
            # ma5 = get_ma5("KRW-BTC")
            # # 15일 이평선
            # ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            # 거래기준 : 5일 이평선
            # print(target_price, current_price, ma5)
            # print("현재가 : " + str(current_price) + " / 매수 목표 : " + str(target_price) +
            #       " / 매도 목표 : " + str(avg_buy * 1.006))
            if target_price < current_price and ma30min < current_price:
                print("매수 포지션: ", current_price, avg_buy, btc)
                if krw > 5000:
                    avg_buy = current_price
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    post_message(myToken, "#alarm",
                                 "매수 목표가 " + str(target_price) + " 달성 / " + " 매수 평균단가 : " + str(avg_buy))

            if btc > 0.00008:
                if current_price >= avg_buy * 1.006:
                    print("point!")
                    sell_result = upbit.sell_market_order(
                        "KRW-BTC", btc*0.9995)
                    post_message(myToken, "#alarm",
                                 "매도 목표가 " + str(avg_buy * 1.006) + " 달성 /" + " 매도 평균단가 : " + str(avg_buy * 1.006))
                    avg_buy = 0
                    time.sleep(180)
                # 스탑로스 기준 : 20% 손실
                elif current_price <= avg_buy * 0.8:
                    sell_result = upbit.sell_market_order(
                        "KRW-BTC", btc*0.9995)
                    post_message(myToken, "#alarm",
                                 "스탑로스 발동, 매도 평균단가 : " + str(avg_buy * 0.8))
                    avg_buy = 0
                    time.sleep(300)

        else:
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                post_message(myToken, "#alarm",
                             "일일 매도 : " + str(sell_result))
        time.sleep(1)

    except Exception as e:
        print(e)
        post_message(myToken, "#alarm", e)
        time.sleep(1)
