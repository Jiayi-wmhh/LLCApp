from django.http import HttpResponse
from django.shortcuts import render
import plotly.graph_objs as go
import numpy as np
import matplotlib.pyplot as plt
from plotly.offline import plot
import pandas as pd
import plotly.express as px
import os
import seaborn as sns
import pymysql
from sshtunnel import SSHTunnelForwarder

def index(request):
    return render(request, 'effect_prime.html')

def data(request):
	utype = request.POST.get('button')
	if utype == 'country':
		country = request.POST.get('country')
		chartname = []
		chartvalue = []
		SSH_BASTION_ADDRESS = '18.221.180.201'  # ここに踏み台のEC2サーバーのIPアドレスを入れる
		# SSH_PORT = 22
		SSH_USER = 'ec2-user'
		SSH_PKEY_PATH = os.path.expanduser('/Users/jiayi/Desktop/webserver_key.pem')  # ここにsshで繋ぐときのキーファイルを指定する
		MYSQL_HOST = 'dev.cc2sysyytboz.us-east-2.rds.amazonaws.com'  # ここにAmazon Aurora MySQLのアドレスを書く
		MYSQL_PORT = 3306
		MYSQL_USER = 'admin'
		MYSQL_PASS = 'Devdb$99'

		with SSHTunnelForwarder(
		        SSH_BASTION_ADDRESS,
		        ssh_username=SSH_USER,
		        ssh_pkey=SSH_PKEY_PATH,
		        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
		) as tunnel:
		    db = pymysql.connect(
		        host='127.0.0.1',
		        user=MYSQL_USER,
		        password=MYSQL_PASS,
		        port=tunnel.local_bind_port
		    )

		    try:
		        with db.cursor() as cur:
		            # cur.execute('SHOW DATABASES')
		            arr = {}
		            cur.execute('select product_name, count(product_name) as count from trade.sales where export_country="%s" group by product_name' %(country))
		            result = cur.fetchall()
		            print(result)
		            length = len(result)
		            for i in range(length):
	            		chartname.append(result[i][0])
	            		chartvalue.append(result[i][1])
		    finally:
		        db.close()
		fig = px.pie(values=chartvalue, names=chartname)
		fig.update_traces(textposition='inside')
		fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide',
		                margin=dict(t=0, b=0, l=0, r=0))
		plot(fig, validate=False, filename='./templates/effect_data.html',
		     auto_open=False)
	elif utype == 'product':
		product = request.POST.get('product')
		chartname = []
		chartvalue = []
		SSH_BASTION_ADDRESS = '18.221.180.201'  # ここに踏み台のEC2サーバーのIPアドレスを入れる
		# SSH_PORT = 22
		SSH_USER = 'ec2-user'
		SSH_PKEY_PATH = os.path.expanduser('/Users/jiayi/Desktop/webserver_key.pem')  # ここにsshで繋ぐときのキーファイルを指定する
		MYSQL_HOST = 'dev.cc2sysyytboz.us-east-2.rds.amazonaws.com'  # ここにAmazon Aurora MySQLのアドレスを書く
		MYSQL_PORT = 3306
		MYSQL_USER = 'admin'
		MYSQL_PASS = 'Devdb$99'

		with SSHTunnelForwarder(
		        SSH_BASTION_ADDRESS,
		        ssh_username=SSH_USER,
		        ssh_pkey=SSH_PKEY_PATH,
		        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
		) as tunnel:
		    db = pymysql.connect(
		        host='127.0.0.1',
		        user=MYSQL_USER,
		        password=MYSQL_PASS,
		        port=tunnel.local_bind_port
		    )

		    try:
		        with db.cursor() as cur:
		            # cur.execute('SHOW DATABASES')
		            arr = {}
		            cur.execute('select export_country, count(export_country) as count from trade.sales where product_name="%s" group by export_country' %(product))
		            result = cur.fetchall()
		            length = len(result)
		            for i in range(length):
	            		chartname.append(result[i][0])
	            		chartvalue.append(result[i][1])
		    finally:
		        db.close()
		fig = px.pie(values=chartvalue, names=chartname)
		fig.update_traces(textposition='inside')
		fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide',
		                margin=dict(t=0, b=0, l=0, r=0))
		plot(fig, validate=False, filename='./templates/effect_data.html',
		     auto_open=False)
	elif utype == 'compare':
		c1 = request.POST.get('compare1')
		Datestart = request.POST.get('Datestart')
		Dateend = request.POST.get('Dateend')
		ss = Datestart[0:4]
		ee = Dateend[0:4]
		pro1 = request.POST.get('product1')
		pro2 = request.POST.get('product2')
		pro3 = request.POST.get('product3')
		pro4 = request.POST.get('product4')
		pro5 = request.POST.get('product5')
		pro6 = request.POST.get('product6')
		context = {"pro1":pro1, "pro2":pro2, "pro3":pro3, "pro4":pro4, "pro5":pro5, "pro6":pro6}
		SSH_BASTION_ADDRESS = '18.221.180.201'  # ここに踏み台のEC2サーバーのIPアドレスを入れる
		# SSH_PORT = 22
		prod_data = []
		prod_data2 = []
		prod_name = []
		SSH_USER = 'ec2-user'
		SSH_PKEY_PATH = os.path.expanduser('/Users/jiayi/Desktop/webserver_key.pem')  # ここにsshで繋ぐときのキーファイルを指定する
		MYSQL_HOST = 'dev.cc2sysyytboz.us-east-2.rds.amazonaws.com'  # ここにAmazon Aurora MySQLのアドレスを書く
		MYSQL_PORT = 3306
		MYSQL_USER = 'admin'
		MYSQL_PASS = 'Devdb$99'

		with SSHTunnelForwarder(
		        SSH_BASTION_ADDRESS,
		        ssh_username=SSH_USER,
		        ssh_pkey=SSH_PKEY_PATH,
		        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
		) as tunnel:
		    db = pymysql.connect(
		        host='127.0.0.1',
		        user=MYSQL_USER,
		        password=MYSQL_PASS,
		        port=tunnel.local_bind_port
		    )

		    try:
		        with db.cursor() as cur:
		            # cur.execute('SHOW DATABASES')
		            arr = {}
		            cur.execute('select product_name, sum(total_sales)  as sum, transaction_year from trade.sales where export_country="%s" and transaction_year>="%s" and transaction_year<="%s" group by transaction_year, product_name' %(c1, ss, ee))
		            result1 = cur.fetchall()
		            diction = {}
		            for i in range(len(result1)):
		            	if(result1[i][0] in diction.keys()):
		            		temp = diction[result1[i][0]]
		            		if (len(temp) < (result1[i][2] - int(ss))):
		            			for i in range(result1[i][2] - int(ss)):
		            				temp.append(0)
		            			diction[result1[i][0]] = temp
		            		diction[result1[i][0]].append(result1[i][1])
		            	else:
		            		temp = []
		            		if(result1[i][2]>int(ss)):
		            			for i in range(result1[i][2] - int(ss)):
		            				temp.append(0)
		            		temp.append(result1[i][1])
		            		diction[result1[i][0]] = temp
		            pro_list = []
		            for i in range(int(ee) - int(ss)+1):
		            	pro_list.append(int(ss)+i)
		            print(diction[pro1])
		            print(type(diction[pro1]))
		            x = pd.DataFrame({"1": diction[pro1],
		            				  "2": diction[pro2],
		            				  "3": diction[pro3],
		            				  "4": diction[pro4],
		            				  "5": diction[pro5],
		            				  "6": diction[pro6]})
		            print(x)
		            plt.figure(figsize=(20, 15))
		            sns.heatmap(x.corr(), annot=True, cmap='Blues', linewidth=0.3);
		            plt.title('Correlation Heatmap', fontdict={'fontsize':12}, pad=12);
		            plt.savefig("./mysite/static/effect.png")
		    #         correlations = x.corr()
		    #         print(correlations)
		    #         sns.heatmap(correlations, annot=True, cmap='Blues', linewidth=0.3)
		    finally:
		        db.close()
	return render(request, 'effect_corr.html', context)