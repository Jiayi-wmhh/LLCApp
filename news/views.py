from django.shortcuts import render
import re
import json
import csv
from io import StringIO
from bs4 import BeautifulSoup
import requests
from urllib import response
from django.http import HttpResponse, HttpResponseRedirect
from urllib.request import urlopen, Request
from requests.structures import CaseInsensitiveDict
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import json
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.offline import plot
from datetime import date
from datetime import timedelta
from datetime import datetime
import numpy as np 

def search(request):
    return render(request,"search.html")

def result(request):
	ticker = request.POST.get('ticker')
	timeRange = request.POST.get('timeRange')
	url_news = "https://finance.yahoo.com/quote/{}?p={}"
	response = requests.get(url_news.format(ticker, ticker))
	soup = BeautifulSoup(response.text)
	terminal = {}
	terminal["stockName"] = ticker
	terminal["statement"] = []
	count = 0
	price = soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
	# change = soup.find('fin-streamer', {'class': 'C($primaryColor) Fz(24px) Fw(b)'}).text
	terminal["price"] = price
	# terminal["change"] = change
	terminal["hyper_spec"] = []
	terminal["nnp"] = []
	peek = 0
	terminal["table"] = []
	yesterday = date.today()-timedelta(days = 1)
	url_news = "https://finviz.com/quote.ashx?t="+ticker
	req = Request(url=url_news,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
	response = urlopen(req)   
	html = BeautifulSoup(response)
	news_table = html.find(id='news-table')
	pieName = ["Negative", "Neutral", "Positive"]
	pieValue = [0, 0, 0]
	for x in news_table.findAll('tr'):
		Statement = x.a.get_text()
		terminal["statement"].append(Statement)
		hyper = x.a.attrs["href"]
		terminal["hyper_spec"].append(hyper)
	for i in terminal["statement"]:
		sid_obj = SentimentIntensityAnalyzer()
		sentiment_dict = sid_obj.polarity_scores(i)
		pieValue[0] += sentiment_dict["neg"]
		pieValue[1] += sentiment_dict["neu"]
		pieValue[2] += sentiment_dict["pos"]
		pieValueSmall = [0, 0, 0, 0, "", ""]
		pieValueSmall[0] = sentiment_dict["neg"]
		pieValueSmall[1] = sentiment_dict["neu"]
		pieValueSmall[2] = sentiment_dict["pos"]
		pieValueSmall[3] = sentiment_dict["compound"]
		pieValueSmall[4] = i
		pieValueSmall[5] = terminal["hyper_spec"][peek]
		peek+=1
		terminal["nnp"].append(pieValueSmall)
	fig = px.pie(values=pieValue, names=pieName, color=pieName,color_discrete_map={'Negative': 'red',
		'Neutral': 'yellow', 'Positive': 'green'})
	fig.update_traces(textposition='inside')
	fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False,)
	# fig.update_layout(showlegend=False)
	plot(fig, validate=False, filename='./LLCApp/templates/newsPie.html', 
		auto_open=False)


	terminal["ticker_list"] = ['AAPL', 'MSFT', 'NVDA', 'V', 'MA', 'AVGO',
	'ADBE', 'CSCO', 'ACN', 'CRM', 'QCOM', 'INTC', 'TXN', 'AMD', 'INTU', 'ORCL', 
	'IBM', 'PYPL', 'ADP', 'AMAT', 'NOW', 'ADI', 'MU', 'LRCX', 'FIS', 'FISV',
	'KLAC', 'SNPS', 'CDNS', 'NXPI', 'ROP', 'ADSK', 'APH', 'FTNT', 'TEL', 'PAYX',
	'MSI', 'MCHP', 'CTSH', 'HPQ', 'GPN', 'ENPH', 'KEYS','GLW','ON','ANET','CDW',
	'ANSS','IT','MPWR','TDY','EPAM', 'BR', 'HPE', 'VRSN', 'ZBRA', 'SWKS', 'FLT',
	'SEDG', 'TRMB', 'TER', 'NTAP', 'PAYC', 'TYL', 'STX', 'AKAM', 'WDC', 'NLOK',
	'JKHY', 'CTXS', 'PTC', 'QRVO', 'FFIV', 'JNPR', 'DXC', 'CDAY']
	terminal["tt_res"] = []
	today = date.today()
	for i in terminal["ticker_list"]:
		url_tt = "https://finviz.com/quote.ashx?t="+i
		req = Request(url=url_tt,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
		response = urlopen(req)   
		soup = BeautifulSoup(response)
		news_tt = soup.find(id='news-table')
		tt_curr = [0.0, 0.0, 0.0, 0.0, i]
		exit_flag = False
		for x in news_tt.findAll('tr'):
			tc = 0
			if len(timeRange) != 0:
				for y in x.find_all('td'):
					if tc == 0 and y.text[0].isalpha():
						yearD = '20'+y.text[7:9]
						if y.text[0:3] == 'Aug':
							monthD = "08"
						elif y.text[0:3] == 'Jul':
							monthD = "07"
						elif y.text[0:3] == 'Jun':
							monthD = "06"
						elif y.text[0:3] == 'May':
							monthD = "05"
						elif y.text[0:3] == 'Apr':
							monthD = "04"
						elif y.text[0:3] == 'Mar':
							monthD = "03"
						elif y.text[0:3] == 'Feb':
							monthD = "02"
						elif y.text[0:3] == 'Jan':
							monthD = "01"
						elif y.text[0:3] == 'Sep':
							monthD = "09"
						elif y.text[0:3] == 'Oct':
							monthD = "03"
						elif y.text[0:3] == 'Nov':
							monthD = "11"
						elif y.text[0:3] == 'Dec':
							monthD = "12"
						dataD = y.text[4:6]
						curr = date(int(yearD), int(monthD), int(dataD))
						diff = (today - curr).days
						if diff > int(timeRange):
							exit_flag = True
							break
					tc+=1
			Statement = x.a.get_text()
			sid_obj = SentimentIntensityAnalyzer()
			sentiment_dict = sid_obj.polarity_scores(Statement)
			tt_curr[0] += sentiment_dict["neg"]
			tt_curr[1] += sentiment_dict["neu"]
			tt_curr[2] += sentiment_dict["pos"]
			tt_curr[3] += sentiment_dict["compound"]
			if exit_flag:
				break
		tt_curr[0] = round(tt_curr[0], 3)
		tt_curr[1] = round(tt_curr[1], 3)
		tt_curr[2] = round(tt_curr[2], 3)
		tt_curr[3] = round(tt_curr[3], 3)
		terminal["tt_res"].append(tt_curr)
	tt_value = [0, 0, 0]
	for i in terminal["tt_res"]:
		tt_value[0] += i[0]
		tt_value[1] += i[1]
		tt_value[2] += i[2]
	fig = px.pie(values=tt_value, names=pieName, color=pieName,color_discrete_map={'Negative': 'red',
		'Neutral': 'yellow', 'Positive': 'green'})
	fig.update_traces(textposition='inside')
	fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False,)
	# fig.update_layout(showlegend=False)
	plot(fig, validate=False, filename='./LLCApp/templates/ttPie.html', 
		auto_open=False)
	cur_bar = [0, 0, 0]
	cur_bar[0] = round(pieValue[0]/(pieValue[0]+pieValue[1]+pieValue[2]), 3)
	cur_bar[1] = round(pieValue[1]/(pieValue[0]+pieValue[1]+pieValue[2]), 3)
	cur_bar[2] = round(pieValue[2]/(pieValue[0]+pieValue[1]+pieValue[2]), 3)
	sum_bar = [0, 0, 0]
	sum_bar[0] = round(tt_value[0]/(tt_value[0]+tt_value[1]+tt_value[2]), 3)
	sum_bar[1] = round(tt_value[1]/(tt_value[0]+tt_value[1]+tt_value[2]), 3)
	sum_bar[2] = round(tt_value[2]/(tt_value[0]+tt_value[1]+tt_value[2]), 3)
	X_axis = np.arange(len(pieName))
	plt.bar(X_axis - 0.2, cur_bar, 0.4, label = ticker)
	plt.bar(X_axis + 0.2, sum_bar, 0.4, label = 'Summary')
	plt.xticks(X_axis, pieName)
	plt.xlabel("Classification")
	plt.ylabel("Value")
	plt.title("News Analysis")
	plt.legend()
	plt.savefig("./LLCApp/LLCApp/static/tt_bar.png")


	return render(request,"result.html", {'terminal':terminal.items()}) 