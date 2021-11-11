import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin

# Create your models here.
class StockAnalysis(models.Model):
    stockTicker = models.CharField('Stock Ticker', max_length=5)
    lastUpdated = models.DateTimeField('Last Updated')
    sentimentScore = models.IntegerField('Sentiment', default=0)
    numTweets = models.IntegerField('Number of Tweets', default=0)
    numPositiveTweets = models.IntegerField('Number of Positive Tweets', default=0)
    numNeutralTweets = models.IntegerField('Number of Neutral Tweets', default=0)
    numNegativeTweets = models.IntegerField('Number of Negative Tweets', default=0)

    def __str__(self):
        return self.stockTicker

    def is_outdated(self):
        return self.lastUpdated <= timezone.now() - datetime.timedelta(minutes=15)


class Author(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1024, default="")
    followers_count = models.IntegerField(default=0)


class Tweet(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=1024) # Greater than we should need
    created_at = models.DateTimeField()
    ticker = models.CharField(max_length=255)
    is_retweet = models.BooleanField()
    retweet_count = models.IntegerField()
    fetched_at = models.DateTimeField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    


class TweetSymbols(models.Model):
    tweet = models.ForeignKey(Tweet, related_name="symbols", on_delete=models.CASCADE)
    symbol = models.CharField(max_length=255)
