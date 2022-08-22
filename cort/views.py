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
	with open('./LLCApp/templates/cort.json', encoding='utf8') as file:
	    data = json.load(file)
	    for obj in data:
	    	terminal["res"].append(obj)
	print(terminal["res"])
	return render(request,"cort.html",{'terminal':terminal.items()})