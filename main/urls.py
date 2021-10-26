from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:sa_stockTicker>', views.stockdetails, name='stockdetails'),
    path('<str:sa_stockTicker>/', views.stockdetails, name='stockdetails'),
    path('twittertest', views.twittertest, name='twittertest')
]