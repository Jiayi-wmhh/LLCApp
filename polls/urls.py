"""LLCApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
	path('prime', views.prime, name='prime'),
    path('multi', views.multi, name='multi'),
    path('first', views.index, name='index'),
    path('oneToAll', views.oneToAll, name='oneToAll'),
    path('second', views.second, name='second'),
    path('showdata', views.showdata, name='showdata'),
    path('showalldata', views.showalldata, name='showalldata'),
    path('mapcolor', views.mapcolor, name='mapcolor'),
    path('mapdata', views.mapdata, name='mapdata'),
]
