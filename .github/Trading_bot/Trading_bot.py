import ccxt
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
import pytz
import tulipy as ti
import time
import os

Apikey=os.getenv('money_printer1_Apikeys')
Apisecret=os.getenv('money_printer1_Apikey')

exchange=ccxt.binance({
'apikey':'Apikey',
'secret':'Apisecret',
'enableRateLimit':True,
'options':{
'defaultType':'futures'}
})
exchange.loadMarkets()

symbol='BTCUSDT'
leverage=75
exchange.setLeverage(leverage,symbol)



def create_since(days,mins):
	timezone=pytz.utc()
	Now=dt.now(timezone)
	since=Now-timedelta(days=1*days,minutes=1*mins)
	starttime=int(since.timestamp()*1000)
	return starttime

def create_endtime():
	timezone=pytz.utc()
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
	df=pd.Dataframe(all_candles,columns=['timestamp','open','high','low','close','volume'])
	data=np.array(df)
	return data

def calculate_mins(timeframe,periods):
			units=timeframe[-1]
			value=float(timeframe[:-1])
			if units== 'm':
				return value *periods
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

def Tconf_Buy(High):
			Tconf=High[-11:]
			return max(Tconf)

def Tconf_sell(low):
			Tconf=low[-11:]
			return min(Tconf)
def quantity(ub,lb,fibbs_value):
	q=ub[-1]-lb[-1]
	Q=fibbs_value/q
	return Q

def check_for_open_orders(symbol):
	try:
		open_orders=exchange.fetchOpenOrders(symbol)
		if len(open_orders)==0:
			return 0
		elif len(open_orders)>0:
			return 1
	except ccxt.NetworkError:
		print('network')
				


		

def place_order(symbol,timeframe,days):
	check=check_for_open_orders(symbol)
	if check==0:
		Data=fetch_data(symbol,timeframe,days,mins=0)
		High=Data[:,2]
		low=Data[:,3]
		close=Data[:,4]
		
		ma5i=calculate_indicators(symbol,timeframe='3m',days=days,indicators='sma',period=5)
		
		ma5ii=calculate_indicators(symbol,timeframe='15m',days=days,indicators='sma',period=5)
		
		ma5iii=calculate_indicators(symbol,timeframe='1h',days=days,indicators='sma',period=5)
		
		bbandi=calculate_indicators(symbol,timeframe='3m',days=days,indicator='bbands',period=10,stddev=2)
		
		bbandii=calculate_indicators(symbol,timeframe='15m',days=days,indicator='bbands',period=10,stddev=2)
		
		bbandiii=calculate_indicators(symbol,timeframe='1h',days=days,indicator='bbands',period=10,stddev=2)
		ma20=calculate_indicators(symbol,timeframe='3m',days=days,indicators='sma',period=20)
		mbi=bbandi[1]
		mbii=bbandii[1]
		mbiii=bbandiii[1]
		lbi=bbandi[0]
		ub=bbandi[2]
		Tconfbuy=Tconf_Buy(High)
		Tconfsell=Tconf_sell(low)
	
	
	Buy_cond1=ma5i[-1] >ma20[-1]
	Buy_cond2=ma5i[-1] >mbi[-1]
	Buy_cond3=ma5ii[-1]>mbii[-1]
	Buy_cond4=ma5iii[-1]>mbiii[-1]
	Buy_cond5=close[-1]>Tconfbuy
	
		
	Sell_cond1=ma5i[-1] <ma20[-1]
	Sell_cond2=ma5i[-1] <mbi[-1]
	Sell_cond3=ma5ii[-1]<mbii[-1]
	Sell_cond4=ma5iii[-1]<mbiii[-1]
	Sell_cond5=close[-1]<Tconfsell
	
	if Buy_cond1 and Buy_cond2 and Buy_cond3 and Buy_cond4 and Buy_cond5:
		return []
def check_positions(symbol):
	try:
		positions=exchange.fetchPositions(symbol)
		if len(positions)>0:
			return positions
		else:
			return []
	except ccxt.NetworkError:
		return []

def close_positions(symbol,timeframe):
	positions=check_positions(symbol)
	if len(positions)>0:
			days=1
			ma5i=calculate_indicators(symbol,timeframe='3m',days=days,indicators='sma',period=5)
			ma20=calculate_indicators(symbol,timeframe='3m',days=days,indicators='sma',period=20)
			
			close_buy_cond1=ma20[-1]>ma5i[-1]
			close_sell_cond1=ma20[-1]<ma5i[-1]
			
			for position in positions:
				amount=position['position Amount']
				side=position['buy']
				if side==['buy'] and close_buy_cond1:
					order =exchange.createOrder(symbol,amount,side='sell')
				elif side==['sell'] and close_sell_cond1:
					order =exchange.createOrder(symbol,amount,side='sell')
					if order :
						return order
	else:
		pass
			
