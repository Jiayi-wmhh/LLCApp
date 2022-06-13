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
from statsmodels.tsa.seasonal import seasonal_decompose
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
	terminal = ({"country": country, "product": product, "Datestart": Datestart,
	"Dateend": Dateend, "percent": percent})
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
	            if len(result) == 0:
	            	return render(request, 'LLC_error.html')
	    finally:
	    	db.close()
	'''
	draw the prediction graph
	'''
	export_sum = []
	year = []
	marr = []
	for i in range(len(data_for_pred)):
		export_sum.append(data_for_pred[i][1])
		year.append(data_for_pred[i][2])
		marr.append(data_for_pred[i])
	if len(data_for_pred)>=24:
		dff = pd.DataFrame(marr, columns = ['Product', 'detail', 'year'])
		plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12])
		plt.figure(figsize=(6.6, 2.6))
		month = seasonal_decompose(dff['detail'], model='multiplicable', period=5)
		plt.title('Seasonal Graph')
		month.seasonal.plot()
		plt.savefig("./LLCApp/LLCApp/static/month.png")
		plt.title('Trend Graph')
		month.trend.plot()
		plt.savefig("./LLCApp/LLCApp/static/trend.png")
	elif len(data_for_pred)<24:
		dff = pd.DataFrame(marr, columns = ['Product', 'detail', 'year'])
		plt.figure(figsize=(6.6, 2.6))
		month = seasonal_decompose(dff['detail'], model='multiplicable', period=5)
		plt.title('Seasonal Graph')
		month.seasonal.plot()
		plt.savefig("./LLCApp/LLCApp/static/month.png")
		plt.title('Trend Graph')
		month.trend.plot()
		plt.savefig("./LLCApp/LLCApp/static/trend.png")
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
    	title="Export Prediction with Linear Regression",
    	xaxis_title="Year",
    	yaxis_title="Export amount",
    	legend_title="Line detail",
    	font=dict(
        	family="Courier New, monospace",
        	size=14,
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
	chartcode = []
	dic = {}
	statename = ['亚洲','欧洲','北美洲','南美洲','非洲','大洋洲']
	statevalue = [0]*6
	together = 0.0
	constract = 0.0
	for i in range(len(result)):
		together = together+result[i][1]
	constract = together * (float(percent)/100)
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
		  chartcode.append("DNK")
		elif i=="俄罗斯":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("RUS")
		elif i=="刚果共和国":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("COD")
		elif i=="印度":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("IND")
		elif i=="印度尼西亚":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("IDN")
		elif i=="土耳其":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("TUR")
		elif i=="塞拉利昂":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("WAL")
		elif i=="墨西哥":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("MEX")
		elif i=="奥地利":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("AUT")
		elif i=="安提瓜和巴布达":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("ATG")
		elif i=="尼日利亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("NGA")
		elif i=="尼泊尔":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("NPL")
		elif i=="巴基斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("PAK")
		elif i=="巴西":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("BRA")
		elif i=="德国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("DEU")
		elif i=="意大利":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("ITA")
		elif i=="挪威":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("NOR")
		elif i=="斯里兰卡":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("LKA")
		elif i=="新加坡":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("SGP")
		elif i=="新西兰":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("NZL")
		elif i=="法国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("FRA")
		elif i=="泰国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("THA")
		elif i=="澳大利亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("AUS")
		elif i=="澳门":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("MAC")
		elif i=="瑞典":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("SWE")
		elif i=="瑞士":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("CHE")
		elif i=="白俄罗斯":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("BLR")
		elif i=="缅甸":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("MMR")
		elif i=="肯尼亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("EAK")
		elif i=="芬兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("FIN")
		elif i=="英国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("GBR")
		elif i=="荷兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("NLD")
		elif i=="菲律宾":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("PHI")
		elif i=="越南":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("VDR")
		elif i=="阿根廷":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("ARG")
		elif i=="韩国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("KOR")
		elif i=="香港":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("HKG")
		elif i=="马来西亚":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("MYS")
		elif i=="中国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("CHN")
		elif i=="乌克兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("UKR")
		elif i=="吉尔吉斯斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("KGZ")
		elif i=="哈萨克斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("KAZ")
		elif i=="土库曼斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("TKM")
		elif i=="波兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("POL")
		elif i=="加纳":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("GHA")
		elif i=="卢旺达":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("RWA")
		elif i=="巴林":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("BHR")
		elif i=="捷克共和国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("CZE")
		elif i=="斯洛文尼亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("SVN")
		elif i=="沙特阿拉伯":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("SAU")
		elif i=="爱尔兰":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("IRL")
		elif i=="突尼斯":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("TUN")
		elif i=="罗马尼亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("ROM")
		elif i=="萨尔瓦多":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("SLV")
		elif i=="西班牙":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("ESP")
		elif i=="孟加拉国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("BGD")
		elif i=="巴拿马":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("PAN")
		elif i=="秘鲁":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("PER")
		elif i=="阿尔及利亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("DZA")
		elif i=="冰岛":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("ISL")
		elif i=="古巴":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("CUB")
		elif i=="哥伦比亚":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("COL")
		elif i=="埃及":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("EGY")
		elif i=="安哥拉":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("AGO")
		elif i=="安道尔":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("AND")
		elif i=="巴拉圭":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("PRY")
		elif i=="布隆迪":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("BDI")
		elif i=="文莱":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("BRU")
		elif i=="格陵兰岛":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("GRL")
		elif i=="法属波利尼西亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("PYF")
		elif i=="爱沙尼亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("EST")
		elif i=="百慕大":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("BMU")
		elif i=="科威特":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("KWT")
		elif i=="老挝":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("LAO")
		elif i=="葡萄牙":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("PRT")
		elif i=="阿富汗":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("AFG")
		elif i=="阿拉伯联合酋长国":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("ARE")
		elif i=="阿曼":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("OMN")
		elif i=="黎巴嫩":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("LBN")
		elif i=="乌拉圭":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("URY")
		elif i=="刚果民主共和国":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("COD")
		elif i=="坦桑尼亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("TZA")
		elif i=="埃塞俄比亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("ETH")
		elif i=="所罗门群岛":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("SLB")
		elif i=="津巴布韦":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("ZWE")
		elif i=="蒙古":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("MNG")
		elif i=="特立尼达和多巴哥共和国":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("TTD")
		elif i=="马达加斯加":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("MDG")
		elif i=="柬埔寨":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("KHM")
		elif i=="马耳他":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("MLT")
		elif i=="科特迪瓦":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("CIV")
		elif i=="苏里南":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("SUR")
		elif i=="保加利亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("BGR")
		elif i=="卡塔尔":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("QAT")
		elif i=="喀麦隆":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("CMR")
		elif i=="科摩罗":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("COM")
		elif i=="莫桑比克":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("MOZ")
		elif i=="吉布提":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("DJI")
		elif i=="塞内加尔":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("SEN")
		elif i=="多米尼克国":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("DMA")
		elif i=="委内瑞拉":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("VEN")
		elif i=="毛里塔尼亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("MRT")
		elif i=="阿塞拜疆":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("AZE")
		elif i=="阿鲁巴岛":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("ABW")
		elif i=="立陶宛":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("LTU")
		elif i=="哥斯达黎加":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("CRI")
		elif i=="巴布亚新几内亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("PNG")
		elif i=="乌兹别克斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("UZB")
		elif i=="乌干达":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("EAU")
		elif i=="克罗地亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("HRV")
		elif i=="几内亚比绍":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("GNB")
		elif i=="塞浦路斯":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("CYP")
		elif i=="尼加拉瓜":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("NIC")
		elif i=="拉脱维亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("LVA")
		elif i=="斯洛伐克":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("SVK")
		elif i=="格林纳达":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("GRD")
		elif i=="海地":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("HTI")
		elif i=="玻利维亚":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("BOL")
		elif i=="索马里":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("SOM")
		elif i=="苏丹":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("SDN")
		elif i=="阿尔巴尼亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("ALB")
		elif i=="马尔代夫":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("MDV")
		elif i=="利比亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("LBY")
		elif i=="尼日尔":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("NER")
		elif i=="布基纳法索":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("BFA")
		elif i=="摩尔多瓦":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("MDA")
		elif i=="摩洛哥":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("MAR")
		elif i=="格鲁吉亚":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("GEO")
		elif i=="几内亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("GIN")
		elif i=="厄瓜多尔":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("ECU")
		elif i=="多哥":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("TGO")
		elif i=="毛里求斯":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("MUS")
		elif i=="马里":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("RMM")
		elif i=="塔吉克斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("TJK")
		elif i=="巴哈马":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("BHS")
		elif i=="贝宁":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("BEN")
		elif i=="马拉维":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("MWI")
		elif i=="多米尼加共和国":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("DOM")
		elif i=="斐济":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("FJI")
		elif i=="洪都拉斯":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("HND")
		elif i=="不丹":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("BTN")
		elif i=="北马其顿共和国":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("MKD")
		elif i=="波斯尼亚和黑塞哥维那":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("BIH")
		elif i=="圣卢西亚":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("LCA")
		elif i=="塞舌尔":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("SYC")
		elif i=="圭亚那":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("GUY")
		elif i=="冈比亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("WAG")
		elif i=="密克罗尼西亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("FSM")
		elif i=="萨摩亚":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("WSM")
		elif i=="圣多美和普林西比":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("STP")
		elif i=="巴巴多斯":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("BDS")
		elif i=="帕劳共和国":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("PLW")
		elif i=="比利时":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("BEL")
		elif i=="卢森堡":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("LUX")
		elif i=="伯利兹":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("BLZ")
		elif i=="圣文森特和格林纳丁斯":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("VCT")
		elif i=="汤加":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("TON")
		elif i=="厄立特里亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("ERI")
		elif i=="南非":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("ZAF")
		elif i=="纳米比亚":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("NAM")
		elif i=="基里巴斯":
		  statevalue[5] = statevalue[5] + simplevalue[index]
		  chartcode.append("KIR")
		elif i=="巴勒斯坦":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("PSE")
		elif i=="美国":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("USA")
		elif i=="博茨瓦纳":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("BWA")
		elif i=="斯威士兰":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("SWZ")
		elif i=="佛得角":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("CPV")
		elif i=="危地马拉":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("GTM")
		elif i=="圣基茨和尼维斯":
		  statevalue[2] = statevalue[2] + simplevalue[index]
		  chartcode.append("KNA")
		elif i=="莱索托":
		  statevalue[4] = statevalue[4] + simplevalue[index]
		  chartcode.append("LSO")
		elif i=="中国台湾":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("TWN")
		elif i=="东帝汶":
		  statevalue[0] = statevalue[0] + simplevalue[index]
		  chartcode.append("TMP")
		elif i=="塞尔维亚":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("SRB")
		elif i=="黑山":
		  statevalue[1] = statevalue[1] + simplevalue[index]
		  chartcode.append("MNE")
		elif i=="库拉索":
		  statevalue[3] = statevalue[3] + simplevalue[index]
		  chartcode.append("CUW")
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
		sort=False)]

	fig = go.Figure(data=data)
	fig.update_traces(textposition='inside')
	fig.update_layout(uniformtext_minsize=9, uniformtext_mode='hide',
                    margin=dict(t=0, b=0, l=0, r=0))
	plot(fig, validate=False, filename='./LLCApp/templates/simplePieChart.html',
         auto_open=False)
	fig = px.bar(x=simplename, y=simplevalue, color=simplename)
	plot(fig, validate=False, filename='./LLCApp/templates/simpleBarChart.html',
         auto_open=False)
	fig = go.Figure(data=go.Choropleth(
		locations = chartcode,
		z = simplevalue,
		colorscale = 'Blues',
		autocolorscale=False,
		# reversescale=True,
		marker_line_color='darkgray',
		marker_line_width=0.5,
    ))
	fig.update_layout(width=650, height=500, margin=dict(t=0, b=0, l=0, r=0))
	plot(fig, validate=False, filename='./LLCApp/templates/fig4.html',
         auto_open=False)
	return render(request, 'graph.html', {'terminal':terminal.items()})