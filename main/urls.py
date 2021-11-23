from django.urls import path, re_path
from . import views
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    re_path(r'^favicon\.ico$', favicon_view),
    path('', views.index, name='index'),
    path('updateHistoricalDatabase', views.updateHistoricalDatabase, name='updateHistoricalDatabase'),
    path('evaluateModel', views.evaluateModel, name='evaluateModel'),
    path('stockAnalysis_json', views.stockAnalysis_json, name='stockAnalysis_json_view'),
    path('textSentimentSpeedTest', views.textSentimentSpeedTest, name='textSentimentSpeedTest'),
    path('<str:sa_stockTicker>', views.stockdetails, name='stockdetails'),
    path('<str:sa_stockTicker>/', views.stockdetails, name='stockdetails'),
    
    
]