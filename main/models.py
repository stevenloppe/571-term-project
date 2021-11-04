import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin

# Create your models here.
class StockAnalysis(models.Model):
    stockTicker = models.CharField('Stock Ticker', max_length=5)
    lastUpdated = models.DateTimeField('Last Updated')
    numTweets = models.IntegerField('Number of Tweets', default=0)
    positiveSentiment = models.IntegerField('Positive Sentiment', default=0)
    negativeSentiment = models.IntegerField('Negative Sentiment', default=0)

    def __str__(self):
        return self.stockTicker

    def is_outdated(self):
        return self.lastUpdated <= timezone.now() - datetime.timedelta(hours=1)
