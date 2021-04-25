import pyupbit

access = "oKn7muzVmQGhOAYxjIPuHJsxD54z83QkDnVk5egl"          # 본인 값으로 변경
secret = "6dyRC8BGCy8HTt1n1bTLnIhiYvyEAfXxdXMIw20g"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-META"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
