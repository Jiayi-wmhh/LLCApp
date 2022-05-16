from django.urls import path

from . import views

urlpatterns = [
	path('', views.homepage, name = 'homepage'),
    path('window', views.window, name='window'),
    path('graph', views.graph, name='graph'),
]