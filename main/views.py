from datetime import date, datetime, timedelta
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render

from main.TextSentiment import textSentiment
from .models import StockAnalysis, Tweet, StockPrice

from twitter import *
from main.twitter_stock import TwitterStock
#from main.twitter_stock import Tweet as TwitterTweet
#from main.twitter_stock import Author as TwitterAuthor

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
    # Moved to stockAnalysis_json()
    return render(request, 'stockdetails.html', {'ticker': sa_stockTicker})


def stockAnalysis_json(request):

    if request.is_ajax and request.method == "GET":
        sa_stockTicker = str(request.GET.get('stockTicker'))

        if sa_stockTicker.endswith("/"):
            sa_stockTicker = sa_stockTicker[:-1]

        try:
            stockAnalysis = StockAnalysis.objects.get(stockTicker = sa_stockTicker)
            if (stockAnalysis.is_outdated() == False):
                stockAnalysis_Json = create_json(stockAnalysis)
                return JsonResponse(stockAnalysis_Json,safe=False,status=200)
        except:
            stockAnalysis = StockAnalysis()

        tweets = Tweet.getTweetsForStock(sa_stockTicker)

        stockAnalysis.stockTicker = sa_stockTicker
        stockAnalysis.lastUpdated = datetime.utcnow()
        stockAnalysis.numTweets = len(tweets)
        
        sentimentScore, numPositive, numNeutral, numNegative, topLikedTweetId, topLikedTweet2Id, topRetweetedTweetId = Tweet.calcSentimentOfTweetSet(tweets)

        stockAnalysis.sentimentScore = sentimentScore
        stockAnalysis.numPositiveTweets = numPositive
        stockAnalysis.numNeutralTweets = numNeutral
        stockAnalysis.numNegativeTweets = numNegative
        stockAnalysis.topLikedTweetId = topLikedTweetId
        stockAnalysis.topLikedTweet2Id = topLikedTweet2Id
        stockAnalysis.topRetweetedTweetId = topRetweetedTweetId

        stockAnalysis.save()

        stockAnalysis_Json = create_json(stockAnalysis)
        return JsonResponse(stockAnalysis_Json,safe=False,status=200)

    # If not is_ajax request
    print("None-ajax request\n")
    return JsonResponse({}, status=400)


def create_json(stockAnalysis):
    return '{ "stockTicker":"'+str(stockAnalysis.stockTicker)+'", "lastUpdated":"'+str(stockAnalysis.lastUpdated)+'", "sentimentScore":"'+str(stockAnalysis.sentimentScore)+'", "numTweets":"'+str(stockAnalysis.numTweets)+'", "numPositiveTweets":"'+str(stockAnalysis.numPositiveTweets)+'", "numNeutralTweets":"'+str(stockAnalysis.numNeutralTweets)+'", "numNegativeTweets":"'+str(stockAnalysis.numNegativeTweets)+'", "topRetweetedTweetId":"'+str(stockAnalysis.topRetweetedTweetId)+'", "topLikedTweetId":"'+str(stockAnalysis.topLikedTweetId)+'", "topLikedTweet2Id":"'+str(stockAnalysis.topLikedTweet2Id)+'"}'






def updateHistoricalDatabase(request):
    try:
        Tweet.updateHistoricalDatabase()    
    except TwitterHTTPError:
        # I guess return what we have so far? 
        return HttpResponse("API Rate Limit")
    
    
    return HttpResponse("Finished")

def updateSentimentForStoredTweets(request):
    Tweet.updateSentimentForDatabaseTweets()

    return HttpResponse("Finished")
    
def updateHistoricalStockPrices(request):
    StockPrice.updateHistoricalStockPrices()

    return HttpResponse("Finished")
    


def evaluateModel(request):
    ticker = request.GET.get('ticker', None)
    startDate = request.GET.get('startDate', None)
    endDate = request.GET.get('endDate', None)

    if ticker is None:
        ticker = "AAPL"

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

    for d in dates:
        todaysTweets = [t for t in tweets if t.created_at.date() == d]
        if(len(todaysTweets) <= 0):
            sentimentScore = 0
        else:   
            sentimentScore, _, _, _, _, _, _ = Tweet.calcSentimentOfTweetSet(todaysTweets)
        
        open,close = StockPrice.getStockPrices(ticker, d)
        topen, tclose = StockPrice.getStockPrices(ticker, (d + timedelta(days=1)))

        is_market_closed = False

        if(open == -1 or topen == -1):
            # market was closed on one of the days so ignore it
            is_market_closed = True
        
        results.append({
            "date": d,
            "sentiment": sentimentScore,
            "isBuy": sentimentScore >= 0,
            "isCorrect": sentimentScore >= 0 and topen > open,
            "today_open": open,
            "tomorrow_open": topen,
            "is_market_closed": is_market_closed,
            "num_tweet_today": len(todaysTweets)

        })

    return render(request, 'evaluateModel.html', {'results' : results, 'ticker': ticker})

def textSentimentSpeedTest(request):
    tweets = Tweet.objects.filter(ticker = "TSLA").order_by("id")[:10]

    start = time.time()

    for tweet in tweets:
        #print(tweet.text)
        #textSentiment(tweet.text)
        tweet.calcSentiment()

    end = time.time()

    return HttpResponse(f"Total Time: {str(end - start)}")
