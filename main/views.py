from datetime import date, datetime, timedelta
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render
from .models import StockAnalysis, Tweet

from twitter import *
from main.twitter_stock import TwitterStock
from main.twitter_stock import Tweet as TwitterTweet
from main.twitter_stock import Author as TwitterAuthor

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
    
    
    sentimentScore, numPositive, numNeutral, numNegative  = calcSentimentOfTweetSet(tweets)

    # positiveSentiment and negativeSentiment are integers, not floats so for now multiplying them by 100 so it isn't saved as 0
    stockAnalysis.sentimentScore = sentimentScore * 100
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


def evaluateModel(request):
    ticker = request.GET.get('ticker', None)
    startDate = request.GET.get('startDate', None)
    endDate = request.GET.get('endDate', None)

    if ticker is None:
        ticker = "APPL"

    if startDate is None:
        startDate = date(2021, 11, 15)
    else:
        startDate = datetime.strptime(startDate, "%Y-%m-%d").date()

    if endDate is None:
        endDate = startDate + timedelta(days = 7)
    else:
        endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
    

    tweets = Tweet.objects.filter(ticker = ticker).filter(created_at__range=[startDate, endDate])

    days = (endDate - startDate).days


    dates = [startDate + timedelta(days=d) for d in range(days)]

    results = []

    thing = []
    for t in tweets:
        thing.append(t)

    for d in dates:
        todaysTweets = [t for t in tweets if t.created_at.date() == d]
        if(len(todaysTweets) <= 0):
            sentimentScore = 0
        else:   
            sentimentScore, _, _, _ = calcSentimentOfTweetSet(todaysTweets)
        
        twitterStock = TwitterStock();
        open,close = twitterStock.getStockPrices(ticker, d)
        topen, tclose = twitterStock.getStockPrices(ticker, (d + timedelta(days=1)))

        if(open == -1 or topen == -1):
            # market was closed on one of the days so ignore it
            pass
        else:
            results.append({
                "date": d,
                "sentiment": sentimentScore,
                "isBuy": sentimentScore >= 0,
                "isCorrect": sentimentScore >= 0 and topen > open,
                "today_open": open,
                "tomorrow_open": topen

            })

    return render(request, 'evaluateModel.html', {'results' : results, 'ticker': ticker})

    




def calcSentimentOfTweetSet(tweets):
    if(isinstance(tweets[0], Tweet)):
        newList = [TwitterTweet(t) for t in tweets]
        tweets = newList

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

    sentimentScore = sentimentSum / len(tweets) 

    return (sentimentScore, numPositive, numNeutral, numNegative)

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