from django.urls import  path
from . import views

urlpatterns = [
    path('',views.mainPage, name = "mainPage"),
    path('stockInfo', views.stockInfo, name = "stockInfo" ),
    path('sentimentAnalysis', views.sentimentAnalysis, name = "sentimentAnalysis" ),
    path('SAresult', views.showSAResult, name = "showSAResult" ),
    path('INFOresult', views.showInfoResult, name = "showInfoResult" ),
]