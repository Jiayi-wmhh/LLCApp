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

def search(request):
    return render(request,"search.html")

def result(request):
	ticker = request.POST.get('ticker')
	url_stats = "https://finance.yahoo.com/quote/{}/key-statistics?p={}"
	url_profile = "https://finance.yahoo.com/quote/{}/profile?p={}"
	url_financials = "https://finance.yahoo.com/quote/{}/financials?p={}"
	url_news = "https://finance.yahoo.com/quote/{}?p={}"
	response = requests.get(url_news.format(ticker, ticker))
	soup = BeautifulSoup(response.text)
	terminal = {}
	terminal["stockName"] = ticker
	terminal["statement"] = []
	count = 0
	price = soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
	change = soup.find('fin-streamer', {'class': 'C($primaryColor) Fz(24px) Fw(b)'}).text
	# for i,item in enumerate(change):
	# 	if i == 10:
	# 		change_amo = item.text
	# 	if i == 11:
	# 		change_per = item.text
	terminal["price"] = price
	terminal["change"] = change
	terminal["hyper_spec"] = []
	# terminal["change_per"] = change_per
	news = soup.find_all('li', class_="js-stream-content Pos(r)")
	for i in news:
		title = i.find('h3', class_="Mb(5px)")
		Statement = title.a.text
		hyper = title.a.attrs["href"]
		hyper = "https://finance.yahoo.com/"+hyper
		terminal["statement"].append(Statement)
		terminal["hyper_spec"].append(hyper)
	pieName = ["Negative", "Neutral", "Positive"]
	pieValue = [0, 0, 0]
	terminal["nnp"] = []
	peek = 0
	for i in terminal["statement"]:
		sid_obj = SentimentIntensityAnalyzer()
		sentiment_dict = sid_obj.polarity_scores(i)
		pieValue[0] += sentiment_dict["neg"]
		pieValue[1] += sentiment_dict["neu"]
		pieValue[2] += sentiment_dict["pos"]
		pieNameSmall = ["Negative", "Neutral", "Positive"]
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
	smallPie = list(range(1, count+1))
	for i in range(1, count+1):
		smallPie[i-1] = "newsPie"+str(i)+".html"
	terminal["smallPie"] = smallPie
	

	url_business = "https://finance.yahoo.com/news/"
	response = requests.get(url_business)
	soup = BeautifulSoup(response.text)
	terminal["business"] = []
	bus_news = soup.find_all('h3', class_="Mb(5px)")
	for i in bus_news:
		bus_title = i.text
		terminal["business"].append(bus_title)
	terminal["nnp_bus"] = []
	pieValueBusiness = [0, 0, 0]
	for i in terminal["business"]:
		sid_obj = SentimentIntensityAnalyzer()
		sentiment_dict = sid_obj.polarity_scores(i)
		pieValueBusiness[0] += sentiment_dict["neg"]
		pieValueBusiness[1] += sentiment_dict["neu"]
		pieValueBusiness[2] += sentiment_dict["pos"]
		bus_value = [0, 0, 0, 0,""]
		bus_value[0] = sentiment_dict["neg"]
		bus_value[1] = sentiment_dict["neu"]
		bus_value[2] = sentiment_dict["pos"]
		bus_value[3] = sentiment_dict["compound"]
		bus_value[4] = i
		terminal["nnp_bus"].append(bus_value)
	figBus = px.pie(values=pieValueBusiness, names=pieName,color=pieName,color_discrete_map={'Negative': 'red',
		'Neutral': 'yellow', 'Positive': 'green'})
	figBus.update_traces(textposition='inside')
	figBus.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False,)
	# fig.update_layout(showlegend=False)
	plot(figBus, validate=False, filename='./LLCApp/templates/newsPieBus.html', 
		auto_open=False)


	line_neg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	line_neu = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	line_pos = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	line_date = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
	for i in range(10):
		line_neg[i] = terminal["nnp"][i][0] + terminal["nnp_bus"][i][0]
		line_neu[i] = terminal["nnp"][i][1] + terminal["nnp_bus"][i][1]
		line_pos[i] = terminal["nnp"][i][2] + terminal["nnp_bus"][i][2]
	plt.plot(line_date, line_neg, 'r', label="Negative")
	plt.plot(line_date, line_neu, 'y', label="Neural")
	plt.plot(line_date, line_pos, 'g', label="Positive")
	plt.xlabel('Days')
	plt.ylabel('Analyze Range')
	plt.savefig("./LLCApp/LLCApp/static/line_graph")

	return render(request,"result.html", {'terminal':terminal.items()}) 