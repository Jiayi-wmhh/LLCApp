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

def search(request):
	terminal = {}
	terminal["res"] = []
	pieName = ["Negative", "Neutral", "Positive"]
	pieValue = [0, 0, 0]
	with open('./LLCApp/templates/cort.json', encoding='utf8') as file:
	    data = json.load(file)
	    for obj in data:
	    	pieValue[0] += obj[0]
	    	pieValue[1] += obj[1]
	    	pieValue[2] += obj[2]
	    	terminal["res"].append(obj)
	fig = px.pie(values=pieValue, names=pieName, color=pieName,color_discrete_map={'Negative': 'red',
		'Neutral': 'yellow', 'Positive': 'green'})
	fig.update_traces(textposition='inside')
	fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False,)
	# fig.update_layout(showlegend=False)
	plot(fig, validate=False, filename='./LLCApp/templates/one_Pie.html', 
		auto_open=False)
	return render(request,"cort.html",{'terminal':terminal.items()})