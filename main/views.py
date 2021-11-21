from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render

from main.TextSentiment import textSentiment
from .models import StockAnalysis, Tweet

from twitter import *
from main.twitter_stock import TwitterStock
from main.twitter_stock import Tweet as TwitterTweet
from main.twitter_stock import Author as TwitterAuthor

import time

TEMPLATE_DIRS = (
    'os.path.join(BASE_DIR, "templates"),'
)


def index(request):

    if request.method == 'GET':
        searchquery = request.GET.get('search', None)
        if type(searchquery) == str:
            return redirect('/'+searchquery)

    return render(request,"index.html")



def stockdetails(request, sa_stockTicker):
    if sa_stockTicker.endswith("/"):
        sa_stockTicker = sa_stockTicker[:-1]

    try:
        stockAnalysis = StockAnalysis.objects.get(stockTicker = sa_stockTicker)
        # TODO: Once we don't need tweets in stockdetails.html check if the stock is out dated
        #if (stock.is_outdated == False):
            #return render(request, 'stockdetails.html', { 'stock' : stockAnalysis, 'tweets': tweets })
    except:
        stockAnalysis = StockAnalysis()

    twitterStock = TwitterStock()
    tweets = twitterStock.getTweetsForStock(sa_stockTicker)
    tweets = analyseTweets(tweets)

    stockAnalysis.stockTicker = sa_stockTicker
    stockAnalysis.lastUpdated = datetime.utcnow()
    stockAnalysis.numTweets = len(tweets)
    
    sentimentSum = 0
    numPositive = 0
    numNeutral = 0
    numNegative = 0

    for t in tweets:
        # Multiplying emoji sentiment weight by 8 so that 1 emoji = 8 characters in text
        new_emojis_len = t.emojis_len * 8
        textWeight = t.text_len / (t.text_len + new_emojis_len)
        emojiWeight = (new_emojis_len / (t.text_len + new_emojis_len))
        sentiment = (t.emoji_sentiment*2-1)*emojiWeight + (t.text_sentiment)*textWeight
        sentimentSum += sentiment
        if sentiment < -0.25:
            numNegative += 1
        elif sentiment < 0.25:
            numNeutral += 1
        else:
            numPositive += 1

    # positiveSentiment and negativeSentiment are integers, not floats so for now multiplying them by 100 so it isn't saved as 0
    stockAnalysis.sentimentScore = (sentimentSum / len(tweets) ) * 100
    stockAnalysis.numPositiveTweets = numPositive
    stockAnalysis.numNeutralTweets = numNeutral
    stockAnalysis.numNegativeTweets = numNegative

    stockAnalysis.save()

    return render(request, 'stockdetails.html', { 'stock' : stockAnalysis, 'tweets': tweets })


def updateHistoricalDatabase(request):
    twitter_stock = TwitterStock()
    try:
        twitter_stock.updateHistoricalDatabase()    
    except TwitterHTTPError:
        # I guess return what we have so far? 
        return HttpResponse("API Rate Limit")
    
    
    return HttpResponse("Finished")


def textSentimentSpeedTest(request):
    tweets = Tweet.objects.filter(ticker = "TSLA").order_by("id")[:10]

    start = time.time()

    for tweet in tweets:
        #print(tweet.text)
        textSentiment(tweet.text)

    end = time.time();

    return HttpResponse(f"Total Time: {str(end - start)}")




def analyseTweets(tweets):
    #TODO: At the moment the tweet analysis happens in the twitter_stock.Tweet constructor
    #       So just returning a list of those objects will "analyse" the tweets.
    #       This is not a very good way of doing this.
    results = []

    for t in tweets:
        #id, created_at, text, ticker, is_retweet, retweet_count, author, symbols
        s = t.symbols.all()
        author = TwitterAuthor(t.author.id, t.author.name, t.author.followers_count)
        tt = TwitterTweet(t.id, t.created_at, t.text, t.ticker, t.is_retweet, t.retweet_count, author, t.symbols.all())
        results.append(tt)

    return results