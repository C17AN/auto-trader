import pyupbit
import numpy as np

# OHLCV = open, high, low, close, volume / 시가, 고가, 저가, 종가, 거래량
df = pyupbit.get_ohlcv("KRW-BTC", count=7)
print(df)

# 변동성 돌파 기준 범위 계산, (고가 - 저가) * k값
df['range'] = (df['high'] - df['low']) * 0.5
# target = 매수가, range 칼럼을 한칸씩 밑으로 내림
df['target'] = df['open'] + df['range'].shift(1)
print(df)

# ror = 수익률, np.where은 조건문, 참일때 값, 거짓일때 값을 인자로 받음.
# high 가 매수가보다 높으면 종가에 전부 매도함
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],
                     1)

# 누적 곱 계산 (cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()

# 하락폭(draw down) 계산 (누적 최대값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
print("MDD(%): ", df['dd'].max())
df.to_excel("dd.xlsx")
