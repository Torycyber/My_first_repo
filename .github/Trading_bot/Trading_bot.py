import ccxt
import pandas as pd
import numpy as np
from datetime import datetime as dt,timedelta
import pytz
import tulipy as ti
import time
import os



Apikey=os.getenv('MY_MONEY_PRINTER1_APIKEY')
Apisecret=os.getenv('MY_MONEY_PRINTER1_APISECRET')

exchange=ccxt.binance({
'apiKey':Apikey,
'secret':Apisecret,
'enableRateLimit':True,
'options':{
	'defaultType':'future'
}
})
exchange.loadMarkets()

symbol='DOGEUSDT'
leverage=50
exchange.setLeverage(leverage,symbol)
fibbs_value=0.5



def create_since(days,mins):
	timezone=pytz.utc
	Now=dt.now(timezone)
	since=Now-timedelta(days=1*days,minutes=1*mins)
	starttime=int(since.timestamp()*1000)
	return starttime

def create_endtime():
	timezone=pytz.utc
	Now=dt.now(timezone)
	end=Now
	endtime=int(end.timestamp()*1000)
	return endtime
	
def fetch_data(symbol,timeframe,days,mins):
	since=create_since(days,mins)
	endtime=create_endtime()
	all_candles=[]
	while since<endtime:
		try:
			candles=exchange.fetchOHLCV(symbol,timeframe,since)
			if not candles:
				break
			all_candles.extend(candles)
			since=int(candles[-1][0]+1)
			if since>=endtime:
				break
		except ccxt.NetworkError as e:
				return []
		time.sleep(1)
	df=pd.DataFrame(all_candles,columns=['timestamp','open','high','low','close','volume'])
	data=np.array(df)
	return data

def calculate_mins(timeframe,periods):
			units=timeframe[-1]
			value=float(timeframe[:-1])
			if units== 'm':
				return value * periods
			if units== 'h':
				return value * periods* 60
			if units== 'd':
				return value * periods * 60 *24

def calculate_indicators(symbol,timeframe,days,indicators,**kwargs):
			period=kwargs.get('period')
			stddev=kwargs.get('stddev')
			mins=calculate_mins(timeframe,period)
			Data=fetch_data(symbol,timeframe,days,mins)
			
			if indicators=='sma':
				ma= ti.sma(Data[:,4],period)
				return ma
			elif indicators=='bbands':
				bbands=ti.bbands(Data[:,4],period,stddev)
				return bbands
			elif indicators=='stoch':
				stoch=ti.stoch(Data[:,2],Data[:,3],Data[:,4],50,3,3)
				return stoch

def Tconf_Buy(High):
			Tconf=High[-20:]
			return max(Tconf)

def Tconf_sell(low):
			Tconf=low[-20:]
			return min(Tconf)


def check_for_open_orders(symbol):
	try:
		open_orders=exchange.fetchOpenOrders(symbol)
		if len(open_orders)==0:
			return 0
		elif len(open_orders)>0:
			return 1
	except ccxt.NetworkError:
		print('network')
				
def current_price(symbol):
	ticker=exchange.fetchTicker(symbol)
	return float(ticker['last'])

def buy_sl(symbol,q,ticker):
	buy_sl=ticker-q
	return exchange.price_to_precision(symbol,buy_sl)

def sell_sl(symbol,q,ticker):
	sell_sl=ticker+q
	return exchange.price_to_precision(symbol,sell_sl)

def Tg_ssl(symbol,q,ticker):
	U=q*0.05
	b=q-U
	tg=ticker+b
	return exchange.price_to_precision(symbol,tg)
def Tg_bsl(symbol,q,ticker):
	U=q*0.05
	b=q-U
	tg=ticker-b
	return exchange.price_to_precision(symbol,tg)

def Tp_buy(symbol,q,ticker):
	b=3*q
	Tp=ticker+b
	return exchange.price_to_precision(symbol,Tp)

def Tp_sell(symbol,q,ticker):
	b=3*q
	tp=ticker-b
	return exchange.price_to_precision(symbol,tp)

		

def place_order(symbol,timeframe,days):
	check=check_for_open_orders(symbol)
	if check==0:
		Data=fetch_data(symbol,timeframe,days,mins=0)
		High=Data[:,2]
		low=Data[:,3]
		close=Data[:,4]

		stoch=calculate_indicators(symbol,timeframe='3m',days=days,indicators='stoch',period=50)
		time.sleep(1)
		
		ma5i=calculate_indicators(symbol,timeframe='3m',days=days,indicators='sma',period=5)
		
		time.sleep(1)
		ma5iii=calculate_indicators(symbol,timeframe='1h',days=days,indicators='sma',period=5)
		
		bbandi=calculate_indicators(symbol,timeframe='3m',days=days,indicator='bbands',period=10,stddev=2)

		
		bbandiii=calculate_indicators(symbol,timeframe='1h',days=days,indicator='bbands',period=10,stddev=2)
		ma20=calculate_indicators(symbol,timeframe='3m',days=days,indicators='sma',period=20)
		mbi=bbandi[1]
		K=stoch[0]
		d=stoch[1]
		mbiii=bbandiii[1]
		lbi=bbandi[0]
		ub=bbandi[2]
		Tconfbuy=Tconf_Buy(High)
	
		Tconfsell=Tconf_sell(low)
	
	
	Buy_cond1=ma5i[-1] >ma20[-1]
	Buy_cond2=ma5i[-1] >mbi[-1]
	Buy_cond4=ma5iii[-1]>mbiii[-1]
	Buy_cond5=close[-1]>Tconfbuy
	Buy_cond3=K[-1] > d[-1] and 30 < K[-1]< 70
	
		
	Sell_cond1=ma5i[-1] <ma20[-1]
	Sell_cond2=ma5i[-1] <mbi[-1]
	Sell_cond3=K[-1] < d[-1]
	Sell_cond4=ma5iii[-1]<mbiii[-1]
	Sell_cond5=close[-1]<Tconfsell

	q=ub[-1]-lbi[-1]
	Amount=fibbs_value/q
	Q=exchange.amount_to_precision(symbol,Amount)
	
	if Buy_cond1 and Buy_cond2 and Buy_cond3 and Buy_cond4 and Buy_cond5:
		order=exchange.create_market_buy_order(symbol,Q)
		ticker=current_price(symbol)
		sl=buy_sl(symbol,q,ticker)
		T_bsl=Tg_bsl(symbol,q,ticker)
		
		Tp=Tp_buy(symbol,q,ticker)

		stoploss_order=exchange.create_stop_limit_order(symbol,'sell',Q,price=sl,stopPrice=T_bsl)
		take_profit=exchange.create_take_profit_order(symbol,'market','sell',Q,price=Tp)
		return order,stoploss_order,take_profit
	elif Sell_cond1 and Sell_cond2 and Sell_cond3 and Sell_cond4 and Sell_cond5:
		order=exchange.create_market_sell_order(symbol,Q)
		sl=sell_sl(symbol,q,ticker)
		T_sll=Tg_ssl(symbol,q,ticker)
		Tp=Tp_sell(symbol,q,ticker)
		stoploss_order=exchange.create_stop_limit_order(symbol,'buy',Q,price=sl,stopPrice=T_sll)
		time.sleep(1)
		take_profit=exchange.create_take_profit_order(symbol,'market','buy',Q,price=Tp)

		return order,stoploss_order,take_profit
def check_positions(symbol):
	try:
		positions=exchange.fetchPositions(symbol)
		if len(positions)>0:
			return positions
		else:
			return []
	except ccxt.NetworkError:
		return []

def close_positions(symbol):
	positions=check_positions(symbol)
	time.sleep(1)
	if len(positions)>0:
			days=1
			ma5i=calculate_indicators(symbol,timeframe='3m',days=days,indicators='sma',period=5)
			ma20=calculate_indicators(symbol,timeframe='3m',days=days,indicators='sma',period=20)
			
			close_buy_cond1=ma20[-1]>ma5i[-1]
			close_sell_cond1=ma20[-1]<ma5i[-1]
			
			for position in positions:
				amount=position['position Amount']
				side=position['side']
				if side=='buy' and close_buy_cond1:
					order =exchange.createMarketOrder(symbol,amount,side='sell')
				elif side=='sell' and close_sell_cond1:
					order =exchange.createMarketOrder(symbol,amount,side='sell')
					if order :
						return order
	else:
		return []
place_trade=place_order(symbol,'3m',days=1,)
close_trade=close_positions(symbol)
