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
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.preprocessing import PolynomialFeatures
def homepage(request):
    return render(request, 'homepage.html')

def window(request):
	return render(request, 'window.html')

def graph(request):
	imex = request.POST.get("imex")
	country = request.POST.get('country')
	product = request.POST.get('product')
	Datestart = request.POST.get('Datestart')
	Dateend = request.POST.get('Dateend')
	percent = request.POST.get('percent')
	terminal = {"country": country, "product": product, "Datestart": Datestart,
	"Dateend": Dateend, "percent": percent}
	SSH_BASTION_ADDRESS = '18.221.180.201'  # ここに踏み台のEC2サーバーのIPアドレスを入れる
	# SSH_PORT = 22
	SSH_USER = 'ec2-user'
	SSH_PKEY_PATH = os.path.expanduser('./LLCApp/templates/webserver_key.pem')  # ここにsshで繋ぐときのキーファイルを指定する
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
	            startD = Datestart[0:4]
	            endD = Datestart[0:4]
	            cur.execute('Select product_name, sum, transaction_year from(Select product_name, sum(total_sales) as sum, transaction_year from trade.sales as temp where export_country="%s" and product_name = "%s" group by transaction_year, product_name order by transaction_year )as res where sum > 0' %(country, product))
	            data_for_pred = cur.fetchall()		
	            cur.execute('select import_country, sum(total_sales) as sale from trade.sales where export_country="%s" and product_name = "%s" and transaction_year >= "%s" and transaction_year <= "%s" group by import_country order by sale desc' %(country, product, startD, endD))
	            result = cur.fetchall()
	    finally:
	    	db.close()
	'''
	draw the prediction graph
	'''
	export_sum = []
	year = []
	for i in range(len(data_for_pred)):
		export_sum.append(data_for_pred[i][1])
		year.append(data_for_pred[i][2])

	x = np.array(year).reshape((-1, 1))
	y = np.array(export_sum)
	polynomial = 1
	transformer = PolynomialFeatures(degree=polynomial)
	transformer.fit(x)
	x_ = transformer.transform(x)

	pred_year = []
	for i in year:
		pred_year.append(i)
	pred_year.append(2021)
	pred_year.append(2022)   



	pred_year_ = np.array(pred_year).reshape((-1, 1))
	transformer.fit(pred_year_)
	predict_year = transformer.transform(pred_year_)



	model = LinearRegression().fit(x_, y)
	pred_sum = model.predict(predict_year)

	fig = go.Figure()              



	fig.add_trace(
	    go.Scatter(
	        x=year,
    		y=export_sum,
 	    	name = "Historical Export Amount"
    ))

	fig.add_trace(
    	go.Line(
        	x=pred_year,
        	y=pred_sum,
        	name = "Predicted Export Amount"
    ))
	fig.update_layout(
    	title="Export Amount Prediction with Linear Regression",
    	xaxis_title="Year",
    	yaxis_title="Export amount",
    	legend_title="Line detail",
    	font=dict(
        	family="Courier New, monospace",
        	size=18,
        	color="RebeccaPurple"
    	)
	)
	plot(fig, validate=False, filename='./LLCApp/templates/prediction.html',
    auto_open=False)

	'''
	draw graph ends
	'''
	simplename = []
	simplevalue = []
	dic = {}
	statename = ['亚洲','欧洲','北美洲','南美洲','非洲','大洋洲']
	statevalue = [0]*6
	together = 0.0
	constract = 0.0
	for i in range(len(result)):
		together = together+result[i][1]
	constract = together * (int(percent)/100)
	for i in range(len(result)):
		if result[i][1] > constract:
			simplename.append(result[i][0])
			simplevalue.append(result[i][1])
			dic.update({ str(i) : result[i] })
	terminal = {**terminal,**dic}
	for i in simplename:
		index = simplename.index(i)
		if i=="丹麦":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="俄罗斯":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="刚果共和国":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="印度":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="印度尼西亚":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="土耳其":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="塞拉利昂":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="墨西哥":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="奥地利":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="安提瓜和巴布达":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="尼日利亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="尼泊尔":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="巴基斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="巴西":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="德国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="意大利":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="挪威":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="斯里兰卡":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="新加坡":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="新西兰":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="法国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="泰国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="澳大利亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="澳门":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="瑞典":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="瑞士":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="白俄罗斯":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="缅甸":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="肯尼亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="芬兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="英国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="荷兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="菲律宾":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="越南":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="阿根廷":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="韩国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="香港":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="马来西亚":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="中国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="乌克兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="吉尔吉斯斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="哈萨克斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="土库曼斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="波兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="加纳":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="卢旺达":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="巴林":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="捷克共和国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="斯洛文尼亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="沙特阿拉伯":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="爱尔兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="突尼斯":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="罗马尼亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="萨尔瓦多":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="西班牙":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="孟加拉国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="巴拿马":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="秘鲁":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="阿尔及利亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="冰岛":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="古巴":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="哥伦比亚":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="埃及":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="安哥拉":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="安道尔":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="巴拉圭":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="布隆迪":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="文莱":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="格陵兰岛":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="法属波利尼西亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="爱沙尼亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="百慕大":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="科威特":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="老挝":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="葡萄牙":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="阿富汗":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="阿拉伯联合酋长国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="阿曼":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="黎巴嫩":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="乌拉圭":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="刚果民主共和国":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="坦桑尼亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="埃塞俄比亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="所罗门群岛":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="津巴布韦":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="蒙古":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="特立尼达和多巴哥共和国":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="马达加斯加":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="柬埔寨":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="马耳他":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="科特迪瓦":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="苏里南":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="保加利亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="卡塔尔":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="喀麦隆":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="科摩罗":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="莫桑比克":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="吉布提":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="塞内加尔":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="多米尼克国":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="委内瑞拉":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="毛里塔尼亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="阿塞拜疆":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="阿鲁巴岛":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="立陶宛":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="哥斯达黎加":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="巴布亚新几内亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="乌兹别克斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="乌干达":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="克罗地亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="几内亚比绍":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="塞浦路斯":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="尼加拉瓜":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="拉脱维亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="斯洛伐克":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="格林纳达":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="海地":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="玻利维亚":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="索马里":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="苏丹":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="阿尔巴尼亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="马尔代夫":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="利比亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="尼日尔":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="布基纳法索":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="摩尔多瓦":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="摩洛哥":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="格鲁吉亚":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="几内亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="厄瓜多尔":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="多哥":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="毛里求斯":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="马里":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="塔吉克斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="巴哈马":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="贝宁":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="马拉维":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="多米尼加共和国":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="斐济":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="洪都拉斯":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="不丹":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="北马其顿共和国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="波斯尼亚和黑塞哥维那":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="圣卢西亚":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="塞舌尔":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="圭亚那":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		elif i=="冈比亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="密克罗尼西亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="萨摩亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="圣多美和普林西比":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="巴巴多斯":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="帕劳共和国":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="比利时":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="卢森堡":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="伯利兹":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="圣文森特和格林纳丁斯":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="汤加":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="厄立特里亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="南非":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="纳米比亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="基里巴斯":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		elif i=="巴勒斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="美国":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="博茨瓦纳":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="斯威士兰":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="佛得角":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="危地马拉":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="圣基茨和尼维斯":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		elif i=="莱索托":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		elif i=="中国台湾":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="东帝汶":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		elif i=="塞尔维亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="黑山":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		elif i=="库拉索":
		  statevalue[3] = statevalue[3] + simplevalue[index]
	outerName = []
	outerValue = []
	for i in range(len(statevalue)):
		if statevalue[i]!=0:
			outerName.append(statename[i])
			outerValue.append(statevalue[i])
	data = [
		go.Pie(values=simplevalue, labels=simplename,
		domain={'x':[0.23,0.77], 'y':[0.23,0.77]},
		direction='clockwise',
		sort=False,
		),

		go.Pie(values=outerValue, labels=outerName,
		domain={'x':[0.1,0.9], 'y':[0,1]},
		hole=0.75,
		direction='clockwise',
		sort=False,
		showlegend=False)]

	fig = go.Figure(data=data)
	fig.update_traces(textposition='inside')
	fig.update_layout(uniformtext_minsize=9, uniformtext_mode='hide',
                    margin=dict(t=0, b=0, l=0, r=0))
	plot(fig, validate=False, filename='./LLCApp/templates/simplePieChart.html',
         auto_open=False)
	fig = px.bar(x=simplename, y=simplevalue, color=simplename)
	plot(fig, validate=False, filename='./LLCApp/templates/simpleBarChart.html',
         auto_open=False)
	chartname = []
	chartvalue = []
	for i in range(len(result)):
		chartname.append(result[i][0])
		chartvalue.append(result[i][1])
	chartcode = []
	for i in chartname:
		if i=="丹麦":
		  chartcode.append("DNK")
		elif i=="俄罗斯":
		  chartcode.append("RUS")
		elif i=="刚果共和国":
		  chartcode.append("COD")
		elif i=="印度":
		  chartcode.append("IND")
		elif i=="印度尼西亚":
		  chartcode.append("IDN")
		elif i=="土耳其":
		  chartcode.append("TUR")
		elif i=="塞拉利昂":
		  chartcode.append("WAL")
		elif i=="墨西哥":
		  chartcode.append("MEX")
		elif i=="奥地利":
		  chartcode.append("AUT")
		elif i=="安提瓜和巴布达":
		  chartcode.append("ATG")
		elif i=="尼日利亚":
		  chartcode.append("NGA")
		elif i=="尼泊尔":
		  chartcode.append("NPL")
		elif i=="巴基斯坦":
		  chartcode.append("PAK")
		elif i=="巴西":
		  chartcode.append("BRA")
		elif i=="德国":
		  chartcode.append("DEU")
		elif i=="意大利":
		  chartcode.append("ITA")
		elif i=="挪威":
		  chartcode.append("NOR")
		elif i=="斯里兰卡":
		  chartcode.append("LKA")
		elif i=="新加坡":
		  chartcode.append("SGP")
		elif i=="新西兰":
		  chartcode.append("NZL")
		elif i=="法国":
		  chartcode.append("FRA")
		elif i=="泰国":
		  chartcode.append("THA")
		elif i=="澳大利亚":
		  chartcode.append("AUS")
		elif i=="澳门":
		  chartcode.append("MAC")
		elif i=="瑞典":
		  chartcode.append("SWE")
		elif i=="瑞士":
		  chartcode.append("CHE")
		elif i=="白俄罗斯":
		  chartcode.append("BLR")
		elif i=="缅甸":
		  chartcode.append("MMR")
		elif i=="肯尼亚":
		  chartcode.append("EAK")
		elif i=="芬兰":
		  chartcode.append("FIN")
		elif i=="英国":
		  chartcode.append("GBR")
		elif i=="荷兰":
		  chartcode.append("NLD")
		elif i=="菲律宾":
		  chartcode.append("PHI")
		elif i=="越南":
		  chartcode.append("VDR")
		elif i=="阿根廷":
		  chartcode.append("ARG")
		elif i=="韩国":
		  chartcode.append("KOR")
		elif i=="香港":
		  chartcode.append("HKG")
		elif i=="马来西亚":
		  chartcode.append("MYS")
		elif i=="中国":
		  chartcode.append("CHN")
		elif i=="乌克兰":
		  chartcode.append("UKR")
		elif i=="吉尔吉斯斯坦":
		  chartcode.append("KGZ")
		elif i=="哈萨克斯坦":
		  chartcode.append("KAZ")
		elif i=="土库曼斯坦":
		  chartcode.append("TKM")
		elif i=="波兰":
		  chartcode.append("POL")
		elif i=="加纳":
		  chartcode.append("GHA")
		elif i=="卢旺达":
		  chartcode.append("RWA")
		elif i=="巴林":
		  chartcode.append("BHR")
		elif i=="捷克共和国":
		  chartcode.append("CZE")
		elif i=="斯洛文尼亚":
		  chartcode.append("SVN")
		elif i=="沙特阿拉伯":
		  chartcode.append("SAU")
		elif i=="爱尔兰":
		  chartcode.append("IRL")
		elif i=="突尼斯":
		  chartcode.append("TUN")
		elif i=="罗马尼亚":
		  chartcode.append("ROM")
		elif i=="萨尔瓦多":
		  chartcode.append("SLV")
		elif i=="西班牙":
		  chartcode.append("ESP")
		elif i=="孟加拉国":
		  chartcode.append("BGD")
		elif i=="巴拿马":
		  chartcode.append("PAN")
		elif i=="秘鲁":
		  chartcode.append("PER")
		elif i=="阿尔及利亚":
		  chartcode.append("DZA")
		elif i=="冰岛":
		  chartcode.append("ISL")
		elif i=="古巴":
		  chartcode.append("CUB")
		elif i=="哥伦比亚":
		  chartcode.append("COL")
		elif i=="埃及":
		  chartcode.append("EGY")
		elif i=="安哥拉":
		  chartcode.append("AGO")
		elif i=="安道尔":
		  chartcode.append("AND")
		elif i=="巴拉圭":
		  chartcode.append("PRY")
		elif i=="布隆迪":
		  chartcode.append("BDI")
		elif i=="文莱":
		  chartcode.append("BRU")
		elif i=="格陵兰岛":
		  chartcode.append("GRL")
		elif i=="法属波利尼西亚":
		  chartcode.append("PYF")
		elif i=="爱沙尼亚":
		  chartcode.append("EST")
		elif i=="百慕大":
		  chartcode.append("BMU")
		elif i=="科威特":
		  chartcode.append("KWT")
		elif i=="老挝":
		  chartcode.append("LAO")
		elif i=="葡萄牙":
		  chartcode.append("PRT")
		elif i=="阿富汗":
		  chartcode.append("AFG")
		elif i=="阿拉伯联合酋长国":
		  chartcode.append("ARE")
		elif i=="阿曼":
		  chartcode.append("OMN")
		elif i=="黎巴嫩":
		  chartcode.append("LBN")
		elif i=="乌拉圭":
		  chartcode.append("URY")
		elif i=="刚果民主共和国":
		  chartcode.append("COD")
		elif i=="坦桑尼亚":
		  chartcode.append("TZA")
		elif i=="埃塞俄比亚":
		  chartcode.append("ETH")
		elif i=="所罗门群岛":
		  chartcode.append("SLB")
		elif i=="津巴布韦":
		  chartcode.append("ZWE")
		elif i=="蒙古":
		  chartcode.append("MNG")
		elif i=="特立尼达和多巴哥共和国":
		  chartcode.append("TTD")
		elif i=="马达加斯加":
		  chartcode.append("MDG")
		elif i=="柬埔寨":
		  chartcode.append("KHM")
		elif i=="马耳他":
		  chartcode.append("MLT")
		elif i=="科特迪瓦":
		  chartcode.append("CIV")
		elif i=="苏里南":
		  chartcode.append("SUR")
		elif i=="保加利亚":
		  chartcode.append("BGR")
		elif i=="卡塔尔":
		  chartcode.append("QAT")
		elif i=="喀麦隆":
		  chartcode.append("CMR")
		elif i=="科摩罗":
		  chartcode.append("COM")
		elif i=="莫桑比克":
		  chartcode.append("MOZ")
		elif i=="吉布提":
		  chartcode.append("DJI")
		elif i=="塞内加尔":
		  chartcode.append("SEN")
		elif i=="多米尼克国":
		  chartcode.append("DMA")
		elif i=="委内瑞拉":
		  chartcode.append("VEN")
		elif i=="毛里塔尼亚":
		  chartcode.append("MRT")
		elif i=="阿塞拜疆":
		  chartcode.append("AZE")
		elif i=="阿鲁巴岛":
		  chartcode.append("ABW")
		elif i=="立陶宛":
		  chartcode.append("LTU")
		elif i=="哥斯达黎加":
		  chartcode.append("CRI")
		elif i=="巴布亚新几内亚":
		  chartcode.append("PNG")
		elif i=="乌兹别克斯坦":
		  chartcode.append("UZB")
		elif i=="乌干达":
		  chartcode.append("EAU")
		elif i=="克罗地亚":
		  chartcode.append("HRV")
		elif i=="几内亚比绍":
		  chartcode.append("GNB")
		elif i=="塞浦路斯":
		  chartcode.append("CYP")
		elif i=="尼加拉瓜":
		  chartcode.append("NIC")
		elif i=="拉脱维亚":
		  chartcode.append("LVA")
		elif i=="斯洛伐克":
		  chartcode.append("SVK")
		elif i=="格林纳达":
		  chartcode.append("GRD")
		elif i=="海地":
		  chartcode.append("HTI")
		elif i=="玻利维亚":
		  chartcode.append("BOL")
		elif i=="索马里":
		  chartcode.append("SOM")
		elif i=="苏丹":
		  chartcode.append("SDN")
		elif i=="阿尔巴尼亚":
		  chartcode.append("ALB")
		elif i=="马尔代夫":
		  chartcode.append("MDV")
		elif i=="利比亚":
		  chartcode.append("LBY")
		elif i=="尼日尔":
		  chartcode.append("NER")
		elif i=="布基纳法索":
		  chartcode.append("BFA")
		elif i=="摩尔多瓦":
		  chartcode.append("MDA")
		elif i=="摩洛哥":
		  chartcode.append("MAR")
		elif i=="格鲁吉亚":
		  chartcode.append("GEO")
		elif i=="几内亚":
		  chartcode.append("GIN")
		elif i=="厄瓜多尔":
		  chartcode.append("ECU")
		elif i=="多哥":
		  chartcode.append("TGO")
		elif i=="毛里求斯":
		  chartcode.append("MUS")
		elif i=="马里":
		  chartcode.append("RMM")
		elif i=="塔吉克斯坦":
		  chartcode.append("TJK")
		elif i=="巴哈马":
		  chartcode.append("BHS")
		elif i=="贝宁":
		  chartcode.append("BEN")
		elif i=="马拉维":
		  chartcode.append("MWI")
		elif i=="多米尼加共和国":
		  chartcode.append("DOM")
		elif i=="斐济":
		  chartcode.append("FJI")
		elif i=="洪都拉斯":
		  chartcode.append("HND")
		elif i=="不丹":
		  chartcode.append("BTN")
		elif i=="北马其顿共和国":
		  chartcode.append("MKD")
		elif i=="波斯尼亚和黑塞哥维那":
		  chartcode.append("BIH")
		elif i=="圣卢西亚":
		  chartcode.append("LCA")
		elif i=="塞舌尔":
		  chartcode.append("SYC")
		elif i=="圭亚那":
		  chartcode.append("GUY")
		elif i=="冈比亚":
		  chartcode.append("WAG")
		elif i=="密克罗尼西亚":
		  chartcode.append("FSM")
		elif i=="萨摩亚":
		  chartcode.append("WSM")
		elif i=="圣多美和普林西比":
		  chartcode.append("STP")
		elif i=="巴巴多斯":
		  chartcode.append("BDS")
		elif i=="帕劳共和国":
		  chartcode.append("PLW")
		elif i=="比利时":
		  chartcode.append("BEL")
		elif i=="卢森堡":
		  chartcode.append("LUX")
		elif i=="伯利兹":
		  chartcode.append("BLZ")
		elif i=="圣文森特和格林纳丁斯":
		  chartcode.append("VCT")
		elif i=="汤加":
		  chartcode.append("TON")
		elif i=="厄立特里亚":
		  chartcode.append("ERI")
		elif i=="南非":
		  chartcode.append("ZAF")
		elif i=="纳米比亚":
		  chartcode.append("NAM")
		elif i=="基里巴斯":
		  chartcode.append("KIR")
		elif i=="巴勒斯坦":
		  chartcode.append("PSE")
		elif i=="美国":
		  chartcode.append("USA")
		elif i=="博茨瓦纳":
		  chartcode.append("BWA")
		elif i=="斯威士兰":
		  chartcode.append("SWZ")
		elif i=="佛得角":
		  chartcode.append("CPV")
		elif i=="危地马拉":
		  chartcode.append("GTM")
		elif i=="圣基茨和尼维斯":
		  chartcode.append("KNA")
		elif i=="莱索托":
		  chartcode.append("LSO")
		elif i=="中国台湾":
		  chartcode.append("TWN")
		elif i=="东帝汶":
		  chartcode.append("TMP")
		elif i=="塞尔维亚":
		  chartcode.append("SRB")
		elif i=="黑山":
		  chartcode.append("MNE")
		elif i=="库拉索":
		  chartcode.append("CUW")
		fig = go.Figure(data=go.Choropleth(
		locations = chartcode,
		z = chartvalue,
		colorscale = 'Blues',
		autocolorscale=False,
		# reversescale=True,
		marker_line_color='darkgray',
		marker_line_width=0.5,
  ))
	fig.update_layout(width=830, height=400,)
	plot(fig, validate=False, filename='./LLCApp/templates/fig4.html',
         auto_open=False)
	lat = []
	lon = []
	text = []
	for i in chartname:
		if i=="丹麦":
		  lat.append(56.26392)
		  lon.append(9.501785)
		  text.append("丹麦 "+str(chartvalue[chartname.index(i)]))
		elif i=="俄罗斯":
		  lat.append(61.52401)
		  lon.append(105.318756)
		  text.append("俄罗斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="刚果共和国":
		  lat.append(-4.038333)
		  lon.append(21.758664)
		  text.append("刚果共和国 "+str(chartvalue[chartname.index(i)]))
		elif i=="印度":
		  lat.append(20.593684)
		  lon.append(78.96288)
		  text.append("印度 "+str(chartvalue[chartname.index(i)]))
		elif i=="印度尼西亚":
		  lat.append(-0.789275)
		  lon.append(113.921327)
		  text.append("印度尼西亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="土耳其":
		  lat.append(38.963745)
		  lon.append(35.243322)
		  text.append("土耳其 "+str(chartvalue[chartname.index(i)]))
		elif i=="塞拉利昂":
		  lat.append(8.460555)
		  lon.append(-11.779889)
		  text.append("塞拉利昂 "+str(chartvalue[chartname.index(i)]))
		elif i=="墨西哥":
		  lat.append(23.634501)
		  lon.append(-102.552784)
		  text.append("墨西哥 "+str(chartvalue[chartname.index(i)]))
		elif i=="奥地利":
		  lat.append(47.516231)
		  lon.append(14.550072)
		  text.append("奥地利 "+str(chartvalue[chartname.index(i)]))
		elif i=="安提瓜和巴布达":
		  lat.append(17.060816)
		  lon.append(-61.796428)
		  text.append("安提瓜和巴布达 "+str(chartvalue[chartname.index(i)]))
		elif i=="尼日利亚":
		  lat.append(9.081999)
		  lon.append(8.675277)
		  text.append("尼日利亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="尼泊尔":
		  lat.append(28.394857)
		  lon.append(84.124008)
		  text.append("尼泊尔 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴基斯坦":
		  lat.append(30.375321)
		  lon.append(69.345116)
		  text.append("巴基斯坦 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴西":
		  lat.append(-14.235004)
		  lon.append(-51.92528)
		  text.append("巴西 "+str(chartvalue[chartname.index(i)]))
		elif i=="德国":
		  lat.append(51.165691)
		  lon.append(10.451526)
		  text.append("德国 "+str(chartvalue[chartname.index(i)]))
		elif i=="意大利":
		  lat.append(41.87194)
		  lon.append(12.56738)
		  text.append("意大利 "+str(chartvalue[chartname.index(i)]))
		elif i=="挪威":
		  lat.append(60.472024)
		  lon.append(8.468946)
		  text.append("挪威 "+str(chartvalue[chartname.index(i)]))
		elif i=="斯里兰卡":
		  lat.append(7.873054)
		  lon.append(80.771797)
		  text.append("斯里兰卡 "+str(chartvalue[chartname.index(i)]))
		elif i=="新加坡":
		  lat.append(1.352083)
		  lon.append(103.819836)
		  text.append("新加坡 "+str(chartvalue[chartname.index(i)]))
		elif i=="新西兰":
		  lat.append(-40.900557)
		  lon.append(174.885971)
		  text.append("新西兰 "+str(chartvalue[chartname.index(i)]))
		elif i=="法国":
		  lat.append(46.227638)
		  lon.append(2.213749)
		  text.append("法国 "+str(chartvalue[chartname.index(i)]))
		elif i=="泰国":
		  lat.append(15.870032)
		  lon.append(100.992541)
		  text.append("泰国 "+str(chartvalue[chartname.index(i)]))
		elif i=="澳大利亚":
		  lat.append(-25.274398)
		  lon.append(133.775136)
		  text.append("澳大利亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="澳门":
		  lat.append(22.198745)
		  lon.append(113.543873)
		  text.append("澳门 "+str(chartvalue[chartname.index(i)]))
		elif i=="瑞典":
		  lat.append(60.128161)
		  lon.append(18.643501)
		  text.append("瑞典 "+str(chartvalue[chartname.index(i)]))
		elif i=="瑞士":
		  lat.append(46.818188)
		  lon.append(8.227512)
		  text.append("瑞士 "+str(chartvalue[chartname.index(i)]))
		elif i=="白俄罗斯":
		  lat.append(53.709807)
		  lon.append(27.953389)
		  text.append("白俄罗斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="缅甸":
		  lat.append(21.913965)
		  lon.append(95.956223)
		  text.append("缅甸 "+str(chartvalue[chartname.index(i)]))
		elif i=="肯尼亚":   
		  lat.append(-0.023559)
		  lon.append(37.906193)
		  text.append("肯尼亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="芬兰":
		  lat.append(61.92411)
		  lon.append(25.748151)
		  text.append("芬兰 "+str(chartvalue[chartname.index(i)]))
		elif i=="英国":
		  lat.append(55.378051)
		  lon.append(-3.435973)
		  text.append("英国 "+str(chartvalue[chartname.index(i)]))
		elif i=="荷兰":
		  lat.append(52.132633)
		  lon.append(5.291266)
		  text.append("荷兰 "+str(chartvalue[chartname.index(i)]))
		elif i=="菲律宾":
		  lat.append(12.879721)
		  lon.append(121.774017)
		  text.append("菲律宾 "+str(chartvalue[chartname.index(i)]))
		elif i=="越南":
		  lat.append(14.058324)
		  lon.append(108.277199)
		  text.append("越南 "+str(chartvalue[chartname.index(i)]))
		elif i=="阿根廷":
		  lat.append(-38.416097)
		  lon.append(-63.616672)
		  text.append("阿根廷 "+str(chartvalue[chartname.index(i)]))
		elif i=="韩国":
		  lat.append(35.907757)
		  lon.append(127.766922)
		  text.append("韩国 "+str(chartvalue[chartname.index(i)]))
		elif i=="香港":
		  lat.append(22.396428)
		  lon.append(114.109497)
		  text.append("香港 "+str(chartvalue[chartname.index(i)]))
		elif i=="马来西亚":
		  lat.append(4.210484)
		  lon.append(101.975766)
		  text.append("马来西亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="中国":
		  lat.append(35.86166)
		  lon.append(104.195397)
		  text.append("中国 "+str(chartvalue[chartname.index(i)]))
		elif i=="乌克兰":
		  lat.append(48.379433)
		  lon.append(31.16558)
		  text.append("乌克兰 "+str(chartvalue[chartname.index(i)]))
		elif i=="吉尔吉斯斯坦":
		  lat.append(41.20438)
		  lon.append(74.766098)
		  text.append("吉尔吉斯斯坦 "+str(chartvalue[chartname.index(i)]))
		elif i=="哈萨克斯坦":
		  lat.append(48.019573)
		  lon.append(66.923684)
		  text.append("哈萨克斯坦 "+str(chartvalue[chartname.index(i)]))
		elif i=="土库曼斯坦":
		  lat.append(38.969719)
		  lon.append(59.556278)
		  text.append("土库曼斯坦 "+str(chartvalue[chartname.index(i)]))
		elif i=="波兰":
		  lat.append(51.919438)
		  lon.append(19.145136)
		  text.append("波兰 "+str(chartvalue[chartname.index(i)]))
		elif i=="加纳":
		  lat.append(7.946527)
		  lon.append(-1.023194)
		  text.append("加纳 "+str(chartvalue[chartname.index(i)]))
		elif i=="卢旺达":
		  lat.append(-1.940278)
		  lon.append(29.873888)
		  text.append("卢旺达 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴林":
		  lat.append(25.930414)
		  lon.append(50.637772)
		  text.append("巴林 "+str(chartvalue[chartname.index(i)]))
		elif i=="捷克共和国":
		  lat.append(49.817492)
		  lon.append(15.472962)
		  text.append("捷克共和国 "+str(chartvalue[chartname.index(i)]))
		elif i=="斯洛文尼亚":
		  lat.append(46.151241)
		  lon.append(14.995463)
		  text.append("斯洛文尼亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="沙特阿拉伯":
		  lat.append(23.885942)
		  lon.append(45.079162)
		  text.append("沙特阿拉伯 "+str(chartvalue[chartname.index(i)]))
		elif i=="爱尔兰":
		  lat.append(53.41291)
		  lon.append(-8.24389)
		  text.append("爱尔兰 "+str(chartvalue[chartname.index(i)]))
		elif i=="突尼斯":
		  lat.append(33.886917)
		  lon.append(9.537499)
		  text.append("突尼斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="罗马尼亚":
		  lat.append(45.943161)
		  lon.append(24.96676)
		  text.append("罗马尼亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="萨尔瓦多":
		  lat.append(13.794185)
		  lon.append(-88.89653)
		  text.append("萨尔瓦多 "+str(chartvalue[chartname.index(i)]))
		elif i=="西班牙":
		  lat.append(40.463667)
		  lon.append(-3.74922)
		  text.append("西班牙 "+str(chartvalue[chartname.index(i)]))
		elif i=="孟加拉国":
		  lat.append(23.684994)
		  lon.append(90.356331)
		  text.append("孟加拉国 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴拿马":
		  lat.append(8.537981)
		  lon.append(-80.782127)
		  text.append("巴拿马 "+str(chartvalue[chartname.index(i)]))
		elif i=="秘鲁":
		  lat.append(9.189967)
		  lon.append(-75.015152)
		  text.append("秘鲁 "+str(chartvalue[chartname.index(i)]))
		elif i=="阿尔及利亚":
		  lat.append(28.033886)
		  lon.append(1.659626)
		  text.append("阿尔及利亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="冰岛":
		  lat.append(64.963051)
		  lon.append(-19.020835)
		  text.append("冰岛 "+str(chartvalue[chartname.index(i)]))
		elif i=="古巴":
		  lat.append(21.521757)
		  lon.append(-77.781167)
		  text.append("古巴 "+str(chartvalue[chartname.index(i)]))
		elif i=="哥伦比亚":
		  lat.append(4.570868)
		  lon.append(-74.297333)
		  text.append("哥伦比亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="埃及":
		  lat.append(26.820553)
		  lon.append(30.802498)
		  text.append("埃及 "+str(chartvalue[chartname.index(i)]))
		elif i=="安哥拉":
		  lat.append(-11.202692)
		  lon.append(17.873887)
		  text.append("安哥拉 "+str(chartvalue[chartname.index(i)]))
		elif i=="安道尔":
		  lat.append(42.546245)
		  lon.append(1.601554)
		  text.append("安道尔 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴拉圭":
		  lat.append(-23.442503)
		  lon.append(-58.443832)
		  text.append("巴拉圭 "+str(chartvalue[chartname.index(i)]))
		elif i=="布隆迪":
		  lat.append(-3.373056)
		  lon.append(29.918886)
		  text.append("布隆迪 "+str(chartvalue[chartname.index(i)]))
		elif i=="文莱":
		  lat.append(4.535277)
		  lon.append(114.727669)
		  text.append("文莱 "+str(chartvalue[chartname.index(i)]))
		elif i=="格陵兰岛":
		  lat.append(71.706936)
		  lon.append(-42.604303)
		  text.append("格陵兰岛 "+str(chartvalue[chartname.index(i)]))
		elif i=="法属波利尼西亚":
		  lat.append(-17.679742)
		  lon.append(-149.406843)
		  text.append("法属波利尼西亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="爱沙尼亚":
		  lat.append(58.595272)
		  lon.append(25.013607)
		  text.append("爱沙尼亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="百慕大":
		  lat.append(32.321384)
		  lon.append(-64.75737)
		  text.append("百慕大 "+str(chartvalue[chartname.index(i)]))
		elif i=="科威特":
		  lat.append(29.31166)
		  lon.append(47.481766)
		  text.append("科威特 "+str(chartvalue[chartname.index(i)]))
		elif i=="老挝":
		  lat.append(19.85627)
		  lon.append(102.495496)
		  text.append("老挝 "+str(chartvalue[chartname.index(i)]))
		elif i=="葡萄牙":
		  lat.append(39.399872)
		  lon.append(-8.224454)
		  text.append("葡萄牙 "+str(chartvalue[chartname.index(i)]))
		elif i=="阿富汗":
		  lat.append(33.93911)
		  lon.append(67.709953)
		  text.append("阿富汗 "+str(chartvalue[chartname.index(i)]))
		elif i=="阿拉伯联合酋长国":
		  lat.append(23.424076)
		  lon.append(53.847818)
		  text.append("阿拉伯联合酋长国 "+str(chartvalue[chartname.index(i)]))
		elif i=="阿曼":
		  lat.append(21.512583)
		  lon.append(55.923255)
		  text.append("阿曼 "+str(chartvalue[chartname.index(i)]))
		elif i=="黎巴嫩":
		  lat.append(33.854721)
		  lon.append(35.862285)
		  text.append("黎巴嫩 "+str(chartvalue[chartname.index(i)]))
		elif i=="乌拉圭":
		  lat.append(-32.522779)
		  lon.append(-55.765835)
		  text.append("乌拉圭 "+str(chartvalue[chartname.index(i)]))
		elif i=="刚果民主共和国":
		  lat.append(-0.228021)
		  lon.append(15.827659)
		  text.append("刚果民主共和国 "+str(chartvalue[chartname.index(i)]))
		elif i=="坦桑尼亚":
		  lat.append(-6.369028)
		  lon.append(34.888822)
		  text.append("坦桑尼亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="埃塞俄比亚":
		  lat.append(9.145)
		  lon.append(40.489673)
		  text.append("埃塞俄比亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="所罗门群岛":
		  lat.append(-9.64571)
		  lon.append(160.156194)
		  text.append("所罗门群岛 "+str(chartvalue[chartname.index(i)]))
		elif i=="津巴布韦":
		  lat.append(-19.015438)
		  lon.append(29.154857)
		  text.append("津巴布韦 "+str(chartvalue[chartname.index(i)]))
		elif i=="蒙古":
		  lat.append(46.862496)
		  lon.append(103.846656)
		  text.append("蒙古 "+str(chartvalue[chartname.index(i)]))
		elif i=="特立尼达和多巴哥共和国":
		  lat.append(10.691803)
		  lon.append(-61.222503)
		  text.append("特立尼达和多巴哥共和国 "+str(chartvalue[chartname.index(i)]))
		elif i=="马达加斯加":
		  lat.append(-18.766947)
		  lon.append(46.869107)
		  text.append("马达加斯加 "+str(chartvalue[chartname.index(i)]))
		elif i=="柬埔寨":
		  lat.append(12.565679)
		  lon.append(104.990963)
		  text.append("柬埔寨 "+str(chartvalue[chartname.index(i)]))
		elif i=="马耳他":
		  lat.append(35.937496)
		  lon.append(14.375416)
		  text.append("马耳他 "+str(chartvalue[chartname.index(i)]))
		elif i=="科特迪瓦":
		  lat.append(7.539989)
		  lon.append(-5.54708)
		  text.append("科特迪瓦 "+str(chartvalue[chartname.index(i)]))
		elif i=="苏里南":
		  lat.append(3.919305)
		  lon.append(-56.027783)
		  text.append("苏里南 "+str(chartvalue[chartname.index(i)]))
		elif i=="保加利亚":
		  lat.append(42.733883)
		  lon.append(25.48583)
		  text.append("保加利亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="卡塔尔":
		  lat.append(25.354826)
		  lon.append(51.183884)
		  text.append("卡塔尔 "+str(chartvalue[chartname.index(i)]))
		elif i=="喀麦隆":
		  lat.append(7.369722)
		  lon.append(12.354722)
		  text.append("喀麦隆 "+str(chartvalue[chartname.index(i)]))
		elif i=="科摩罗":
		  lat.append(-11.875001)
		  lon.append(43.872219)
		  text.append("科摩罗 "+str(chartvalue[chartname.index(i)]))
		elif i=="莫桑比克":
		  lat.append(-18.665695)
		  lon.append(35.529562)
		  text.append("莫桑比克 "+str(chartvalue[chartname.index(i)]))
		elif i=="吉布提":
		  lat.append(11.825138)
		  lon.append(42.590275)
		  text.append("吉布提 "+str(chartvalue[chartname.index(i)]))
		elif i=="塞内加尔":
		  lat.append(14.497401)
		  lon.append(-14.452362)
		  text.append("塞内加尔 "+str(chartvalue[chartname.index(i)]))
		elif i=="多米尼克国":
		  lat.append(15.414999)
		  lon.append(-61.370976)
		  text.append("多米尼克国 "+str(chartvalue[chartname.index(i)]))
		elif i=="委内瑞拉":
		  lat.append(6.42375)
		  lon.append(-66.58973)
		  text.append("委内瑞拉 "+str(chartvalue[chartname.index(i)]))
		elif i=="毛里塔尼亚":
		  lat.append(21.00789)
		  lon.append(-10.940835)
		  text.append("毛里塔尼亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="阿塞拜疆":
		  lat.append(40.143105)
		  lon.append(47.576927)
		  text.append("阿塞拜疆 "+str(chartvalue[chartname.index(i)]))
		elif i=="阿鲁巴岛":
		  lat.append(12.52111)
		  lon.append(-69.968338)
		  text.append("阿鲁巴岛 "+str(chartvalue[chartname.index(i)]))
		elif i=="立陶宛":
		  lat.append(55.169438)
		  lon.append(23.881275)
		  text.append("立陶宛 "+str(chartvalue[chartname.index(i)]))
		elif i=="哥斯达黎加":
		  lat.append(9.748917)
		  lon.append(-83.753428)
		  text.append("哥斯达黎加 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴布亚新几内亚":
		  lat.append(-6.314993)
		  lon.append(143.95555)
		  text.append("巴布亚新几内亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="乌兹别克斯坦":
		  lat.append(41.377491)
		  lon.append(64.585262)
		  text.append("乌兹别克斯坦 "+str(chartvalue[chartname.index(i)]))
		elif i=="乌干达":
		  lat.append(1.373333)
		  lon.append(32.290275)
		  text.append("乌干达 "+str(chartvalue[chartname.index(i)]))
		elif i=="克罗地亚":
		  lat.append(45.1)
		  lon.append(15.2)
		  text.append("克罗地亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="几内亚比绍":
		  lat.append(11.803749)
		  lon.append(-15.180413)
		  text.append("几内亚比绍 "+str(chartvalue[chartname.index(i)]))
		elif i=="塞浦路斯":
		  lat.append(35.126413)
		  lon.append(33.429859)
		  text.append("塞浦路斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="尼加拉瓜":
		  lat.append(12.865416)
		  lon.append(-85.207229)
		  text.append("尼加拉瓜 "+str(chartvalue[chartname.index(i)]))
		elif i=="拉脱维亚":
		  lat.append(56.879635)
		  lon.append(24.603189)
		  text.append("拉脱维亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="斯洛伐克":
		  lat.append(48.669026)
		  lon.append(19.699024)
		  text.append("斯洛伐克 "+str(chartvalue[chartname.index(i)]))
		elif i=="格林纳达":
		  lat.append(12.262776)
		  lon.append(-61.604171)
		  text.append("格林纳达 "+str(chartvalue[chartname.index(i)]))
		elif i=="海地":
		  lat.append(18.971187)
		  lon.append(-72.285215)
		  text.append("海地 "+str(chartvalue[chartname.index(i)]))
		elif i=="玻利维亚":
		  lat.append(-16.290154)
		  lon.append(-63.588653)
		  text.append("玻利维亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="索马里":
		  lat.append(5.152149)
		  lon.append(46.199616)
		  text.append("索马里 "+str(chartvalue[chartname.index(i)]))
		elif i=="苏丹":
		  lat.append(12.862807)
		  lon.append(30.217636)
		  text.append("苏丹 "+str(chartvalue[chartname.index(i)]))
		elif i=="阿尔巴尼亚":
		  lat.append(41.153332)
		  lon.append(20.168331)
		  text.append("阿尔巴尼亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="马尔代夫":
		  lat.append(3.202778)
		  lon.append(73.22068)
		  text.append("马尔代夫 "+str(chartvalue[chartname.index(i)]))
		elif i=="利比亚":
		  lat.append(26.3351)
		  lon.append(17.228331)
		  text.append("利比亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="尼日尔":
		  lat.append(17.607789)
		  lon.append(8.081666)
		  text.append("尼日尔 "+str(chartvalue[chartname.index(i)]))
		elif i=="布基纳法索":
		  lat.append(12.238333)
		  lon.append(-1.561593)
		  text.append("布基纳法索 "+str(chartvalue[chartname.index(i)]))
		elif i=="摩尔多瓦":
		  lat.append(47.411631)
		  lon.append(28.369885)
		  text.append("摩尔多瓦 "+str(chartvalue[chartname.index(i)]))
		elif i=="摩洛哥":
		  lat.append(31.791702)
		  lon.append(-7.09262)
		  text.append("摩洛哥 "+str(chartvalue[chartname.index(i)]))
		elif i=="格鲁吉亚":
		  lat.append(42.315407)
		  lon.append(43.356892)
		  text.append("格鲁吉亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="几内亚":
		  lat.append(9.945587)
		  lon.append(-9.696645)
		  text.append("几内亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="厄瓜多尔":
		  lat.append(-1.831239)
		  lon.append(-78.183406)
		  text.append("厄瓜多尔 "+str(chartvalue[chartname.index(i)]))
		elif i=="多哥":
		  lat.append(8.619543)
		  lon.append(0.824782)
		  text.append("多哥 "+str(chartvalue[chartname.index(i)]))
		elif i=="毛里求斯":
		  lat.append(-20.348404)
		  lon.append(57.552152)
		  text.append("毛里求斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="马里":
		  lat.append(17.570692)
		  lon.append(-3.996166)
		  text.append("马里 "+str(chartvalue[chartname.index(i)]))
		elif i=="塔吉克斯坦":
		  lat.append(38.861034)
		  lon.append(71.276093)
		  text.append("塔吉克斯坦 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴哈马":
		  lat.append(25.03428)
		  lon.append(-77.39628)
		  text.append("巴哈马 "+str(chartvalue[chartname.index(i)]))
		elif i=="贝宁":
		  lat.append(9.30769)
		  lon.append(2.315834)
		  text.append("贝宁 "+str(chartvalue[chartname.index(i)]))
		elif i=="马拉维":
		  lat.append(-13.254308)
		  lon.append(34.301525)
		  text.append("马拉维 "+str(chartvalue[chartname.index(i)]))
		elif i=="多米尼加共和国":
		  lat.append(18.735693)
		  lon.append(-70.162651)
		  text.append("多米尼加共和国 "+str(chartvalue[chartname.index(i)]))
		elif i=="斐济":
		  lat.append(-16.578193)
		  lon.append(179.414413)
		  text.append("斐济 "+str(chartvalue[chartname.index(i)]))
		elif i=="洪都拉斯":
		  lat.append(15.199999)
		  lon.append(-86.241905)
		  text.append("洪都拉斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="不丹":
		  lat.append(27.514162)
		  lon.append(90.433601)
		  text.append("不丹 "+str(chartvalue[chartname.index(i)]))
		elif i=="北马其顿共和国":
		  lat.append(41.608635)
		  lon.append(21.745275)
		  text.append("北马其顿共和国 "+str(chartvalue[chartname.index(i)]))
		elif i=="波斯尼亚和黑塞哥维那":
		  lat.append(43.915886)
		  lon.append(17.679076)
		  text.append("波斯尼亚和黑塞哥维那 "+str(chartvalue[chartname.index(i)]))
		elif i=="圣卢西亚":
		  lat.append(13.909444)
		  lon.append(-60.978893)
		  text.append("圣卢西亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="塞舌尔":
		  lat.append(-4.679574)
		  lon.append(55.491977)
		  text.append("塞舌尔 "+str(chartvalue[chartname.index(i)]))
		elif i=="圭亚那":
		  lat.append(4.860416)
		  lon.append(-58.93018)
		  text.append("圭亚那 "+str(chartvalue[chartname.index(i)]))
		elif i=="冈比亚":
		  lat.append(13.443182)
		  lon.append(-15.310139)
		  text.append("冈比亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="密克罗尼西亚":
		  lat.append(7.425554)
		  lon.append(150.550812)
		  text.append("密克罗尼西亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="萨摩亚":
		  lat.append(-13.759029)
		  lon.append(-172.104629)
		  text.append("萨摩亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="圣多美和普林西比":
		  lat.append(0.18636)
		  lon.append(6.613081)
		  text.append("圣多美和普林西比 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴巴多斯":
		  lat.append(13.193887)
		  lon.append(-59.543198)
		  text.append("巴巴多斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="帕劳共和国":
		  lat.append(7.51498)
		  lon.append(134.58252)
		  text.append("帕劳共和国 "+str(chartvalue[chartname.index(i)]))
		elif i=="比利时":
		  lat.append(50.503887)
		  lon.append(4.469936)
		  text.append("比利时 "+str(chartvalue[chartname.index(i)]))
		elif i=="卢森堡":
		  lat.append(49.815273)
		  lon.append(6.129583)
		  text.append("卢森堡 "+str(chartvalue[chartname.index(i)]))
		elif i=="伯利兹":
		  lat.append(17.189877)
		  lon.append(-88.49765)
		  text.append("伯利兹 "+str(chartvalue[chartname.index(i)]))
		elif i=="圣文森特和格林纳丁斯":
		  lat.append(12.984305)
		  lon.append(-61.287228)
		  text.append("圣文森特和格林纳丁斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="汤加":
		  lat.append(-21.178986)
		  lon.append(-175.198242)
		  text.append("汤加 "+str(chartvalue[chartname.index(i)]))
		elif i=="厄立特里亚":
		  lat.append(15.179384)
		  lon.append(39.782334)
		  text.append("厄立特里亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="南非":
		  lat.append(-30.559482)
		  lon.append(22.937506)
		  text.append("南非 "+str(chartvalue[chartname.index(i)]))
		elif i=="纳米比亚":
		  lat.append(-22.95764)
		  lon.append(18.49041)
		  text.append("纳米比亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="基里巴斯":
		  lat.append(-3.370417)
		  lon.append(-168.734039)
		  text.append("基里巴斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="巴勒斯坦":
		  lat.append(31.952162)
		  lon.append(35.233154)
		  text.append("巴勒斯坦 "+str(chartvalue[chartname.index(i)]))
		elif i=="美国":
		  lat.append(37.09024)
		  lon.append(95.712891)
		  text.append("美国 "+str(chartvalue[chartname.index(i)]))
		elif i=="博茨瓦纳":
		  lat.append(-22.328474)
		  lon.append(24.684866)
		  text.append("博茨瓦纳 "+str(chartvalue[chartname.index(i)]))
		elif i=="斯威士兰":
		  lat.append(-26.522503)
		  lon.append(31.465866)
		  text.append("斯威士兰 "+str(chartvalue[chartname.index(i)]))
		elif i=="佛得角":
		  lat.append(16.002082)
		  lon.append(-24.013197)
		  text.append("佛得角 "+str(chartvalue[chartname.index(i)]))
		elif i=="危地马拉":
		  lat.append(15.783471)
		  lon.append(-90.230759)
		  text.append("危地马拉 "+str(chartvalue[chartname.index(i)]))
		elif i=="圣基茨和尼维斯":
		  lat.append(17.357822)
		  lon.append(-62.782998)
		  text.append("圣基茨和尼维斯 "+str(chartvalue[chartname.index(i)]))
		elif i=="莱索托":
		  lat.append(-29.609988)
		  lon.append(28.233608)
		  text.append("莱索托 "+str(chartvalue[chartname.index(i)]))
		elif i=="中国台湾":
		  lat.append(23.69781)
		  lon.append(120.960515)
		  text.append("中国台湾 "+str(chartvalue[chartname.index(i)]))
		elif i=="东帝汶":
		  lat.append(-8.874217)
		  lon.append(125.727539)
		  text.append("东帝汶 "+str(chartvalue[chartname.index(i)]))
		elif i=="塞尔维亚":
		  lat.append(44.016521)
		  lon.append(21.005859)
		  text.append("塞尔维亚 "+str(chartvalue[chartname.index(i)]))
		elif i=="黑山":
		  lat.append(42.708678)
		  lon.append(19.37439)
		  text.append("黑山 "+str(chartvalue[chartname.index(i)]))
		elif i=="库拉索":
		  lat.append(-68.9405465)
		  lon.append(12.1094497)
		  text.append("库拉索 "+str(chartvalue[chartname.index(i)]))
	fig = go.Figure(go.Scattergeo(
	    lat=lat,
	    lon=lon,
	    text=text,
	    mode='text',
	    textfont=dict(
	                size=8,
	                color='red'
	                ),
	    hoverinfo='skip',
	    marker_color='red'))
	fig.update_geos(projection_type="natural earth")
	fig.update_layout(width=900, height=400,
	                # title_x=0.5,
	                geo=dict(
	                    projection_type='natural earth',
	                    center_lon=-180,
	                    center_lat=0,
	                    projection_rotation_lon=-180,
	                    showland=True,
	                    showcountries=True,
	                    landcolor='rgb(135,206,250)',
	                    bgcolor='rgba(0,0,0,0)',
	                    countrycolor='rgb(30,144,255)'
	                ),
	                )
	plot(fig, validate=False, filename='./LLCApp/templates/fig6.html',
	     auto_open=False)
	return render(request, 'graph.html', terminal)