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
import time

terminal["ticker_list"] = ['AAPL', 'MSFT', 'NVDA', 'V', 'MA', 'AVGO',
	'ADBE', 'CSCO', 'ACN', 'CRM', 'QCOM', 'INTC', 'TXN', 'AMD', 'INTU', 'ORCL', 
	'IBM', 'PYPL', 'ADP', 'AMAT', 'NOW', 'ADI', 'MU', 'LRCX', 'FIS', 'FISV',
	'KLAC', 'SNPS', 'CDNS', 'NXPI', 'ROP', 'ADSK', 'APH', 'FTNT', 'TEL', 'PAYX',
	'MSI', 'MCHP', 'CTSH', 'HPQ', 'GPN', 'ENPH', 'KEYS','GLW','ON','ANET','CDW',
	'ANSS','IT','MPWR','TDY','EPAM', 'BR', 'HPE', 'VRSN', 'ZBRA', 'SWKS', 'FLT',
	'SEDG', 'TRMB', 'TER', 'NTAP', 'PAYC', 'TYL', 'STX', 'AKAM', 'WDC', 'NLOK',
	'JKHY', 'CTXS', 'PTC', 'QRVO', 'FFIV', 'JNPR', 'DXC', 'CDAY']
terminal["tt_res"] = []
for i in terminal["ticker_list"]:
	url_tt = "https://finviz.com/quote.ashx?t="+i
	req = Request(url=url_tt,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
	response = urlopen(req)   
	soup = BeautifulSoup(response)
	news_tt = soup.find(id='news-table')
	tt_curr = [0.0, 0.0, 0.0, 0.0, i]
	for x in news_tt.findAll('tr'):
		Statement = x.a.get_text()
		sid_obj = SentimentIntensityAnalyzer()
		sentiment_dict = sid_obj.polarity_scores(Statement)
		tt_curr[0] += sentiment_dict["neg"]
		tt_curr[1] += sentiment_dict["neu"]
		tt_curr[2] += sentiment_dict["pos"]
		tt_curr[3] += sentiment_dict["compound"]
	tt_curr[0] = round(tt_curr[0], 3)
	tt_curr[1] = round(tt_curr[1], 3)
	tt_curr[2] = round(tt_curr[2], 3)
	tt_curr[3] = round(tt_curr[3], 3)
	terminal["tt_res"].append(tt_curr)
print(terminal["tt_res"])
