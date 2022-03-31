from urllib import response
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import re
from requests.structures import CaseInsensitiveDict
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
import json
from datetime import date,timedelta
from dateutil.relativedelta import *
import time
# Create your views here.

def search(request):
    return render(request,"stock/search.html")

def result(request):
    ticker = request.POST.get('ticker')
    ticker = str(ticker).upper()
    apikey = "&token=c8kjg9qad3ibbdm3takg"
    res = []

    #company detail
    company_base_url = "https://finnhub.io/api/v1/stock/profile2?symbol="
    company_base_url += ticker
    company_base_url += apikey
    resp1 = requests.get(company_base_url).json()
    resp1 = json.dumps(resp1)
    res.append(resp1)

    #company summary
    summary_base_url = "https://finnhub.io/api/v1/quote?symbol="
    summary_base_url += ticker
    summary_base_url += apikey
    resp2 = requests.get(summary_base_url).json()
    resp2 = json.dumps(resp2)
    res.append(resp2)

    #company news

    news_base_url = "https://finnhub.io/api/v1/company-news?symbol="
    news_base_url += ticker
    current_date = date.today().isoformat() 
    days_before = (date.today()-timedelta(days=3)).isoformat()
    news_base_url += "&from=" + days_before +"&to=" + current_date
    news_base_url += apikey
    resp3 = requests.get(news_base_url).json()
    resp3 = json.dumps(resp3)
    res.append(resp3)

    #company chart

    chart_base_url = "https://finnhub.io/api/v1/stock/candle?symbol="
    chart_base_url += ticker
    chart_base_url += "&resolution=D"
    current_date = date.today()
    days_before = current_date + relativedelta(months=-6,days=-1)
    chart_base_url += "&from=" + str(int(time.mktime(days_before.timetuple()))) +"&to=" + str(int(time.mktime(current_date.timetuple())))
    chart_base_url += apikey
    resp4 = requests.get(chart_base_url).json()
    resp4 = json.dumps(resp4)
    res.append(resp4)
    
    # twitter
    num_twitter = 100
    # change bearer token when the company account is created
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAM48aAEAAAAAi%2FLi%2ByJN40pC0y39uAGACG8joMw%3DWSvLjUQofW6rPSZoNaC9QWdJQfXy8EtTWdaUSIFePc4VWyT4mP"
    url = "https://api.twitter.com/2/tweets/search/recent?query="+ticker+"&max_results="+str(num_twitter)
    # add headers information to get request
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + bearer_token


    resp = requests.get(url, headers=headers).json()
    data = resp["data"]
    tweets = []

    for i in range(len(data)):
        parsed_tweet =[]
        parsed_tweet.append(ticker)
        tweet = data[i]["text"]
        parsed_tweet.append(tweet)
        tweets.append(parsed_tweet)

    columns = ['ticker','text']
    df = pd.DataFrame(tweets,columns=columns)
    vader = SentimentIntensityAnalyzer()
    # Iterate through the headlines and get the polarity scores using vader
    scores = df['text'].apply(vader.polarity_scores).tolist()
    # Convert the 'scores' list of dicts into a DataFrame
    scores_df = pd.DataFrame(scores)
    # Join the DataFrames of the news and the list of dicts
    df = df.join(scores_df, rsuffix='_right')
    result = df.to_json(orient = "records")
    result_json = json.dumps(result)
    res.append(result_json)

    # finviz

    finwiz_url = 'https://finviz.com/quote.ashx?t='
    news_tables = {}
    # add required ticker inside tickers list
    tickers = []
    tickers.append(ticker)

    for Ticker in tickers:
        url = finwiz_url + Ticker
        req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
        response = urlopen(req)    
        # Read the contents of the file into 'html'
        html = BeautifulSoup(response)
        # Find 'news-table' in the Soup and load it into 'news_table'
        news_table = html.find(id='news-table')
        # Add the table to our dictionary
        news_tables[Ticker] = news_table


    parsed_news = []

    # Iterate through the news
    for file_name, news_table in news_tables.items():
        # Iterate through all tr tags in 'news_table'
        for x in news_table.findAll('tr'):
            # read the text from each tr tag into text
            # get text from a only
            text = x.a.get_text() 
            # splite text in the td tag into a list 
            date_scrape = x.td.text.split()
            # if the length of 'date_scrape' is 1, load 'time' as the only element

            if len(date_scrape) == 1:
                news_time = date_scrape[0]
                
            # else load 'date' as the 1st element and 'time' as the second    
            else:
                news_date = date_scrape[0]
                news_time = date_scrape[1]
            # Extract the ticker from the file name, get the string up to the 1st '_'  
            ticker = file_name.split('_')[0]
            
            # Append ticker, date, time and headline as a list to the 'parsed_news' list
            parsed_news.append([ticker, news_date, news_time, text])
            
    vader = SentimentIntensityAnalyzer()

    # Set column names
    columns = ['ticker', 'date', 'time', 'text']

    # Convert the parsed_news list into a DataFrame called 'parsed_and_scored_news'
    parsed_and_scored_news = pd.DataFrame(parsed_news, columns=columns)

    # Iterate through the headlines and get the polarity scores using vader
    scores = parsed_and_scored_news['text'].apply(vader.polarity_scores).tolist()

    # Convert the 'scores' list of dicts into a DataFrame
    scores_df = pd.DataFrame(scores)

    # Join the DataFrames of the news and the list of dicts
    parsed_and_scored_news = parsed_and_scored_news.join(scores_df, rsuffix='_right')

    # Convert the date column from string to datetime
    parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date
    parsed_and_scored_news = parsed_and_scored_news.to_json(orient = "records")
    result_json = json.dumps(parsed_and_scored_news)
    res.append(result_json)

    return render(request,"stock/result.html",{ "Result":res }) 
