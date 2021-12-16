from datetime import date, datetime, timedelta
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render
from main.AnalysisEvaluation import AnalysisList

from main.TextSentiment import textSentiment
from .models import BIG_TICKERS, StockAnalysis, Tweet, StockPrice

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

    analyses = StockAnalysis.objects.order_by('-lastUpdated')[:5]
    # asSeRtiOnErRoR: nEgaTivE iNdexInG iS nOt SuPpRorTeD :D
    #analyses = orderedStocks[len(orderedStocks)-5:]


    return render(request,"index.html", {'analyses' : analyses})


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
    tickers = request.GET.get('tickers', None)
    startDate = request.GET.get('startDate', None)
    endDate = request.GET.get('endDate', None)

    if tickers is None:
        tickers = ["AAPL"]
    else:

        if(tickers=="__ALL__"):
            # If a magic value is sent in then we evaluate ALL of the tickers in our system
            tickers = BIG_TICKERS
        else:
            # split comma separated string into list and trim off whitespace
            tickers = [ticker.strip().upper() for ticker in tickers.split(',')]
        

    if startDate is None:
        startDate = date(2021, 11, 15)
    else:
        startDate = datetime.strptime(startDate, "%Y-%m-%d").date()

    if endDate is None:
        endDate = startDate + timedelta(days = 7)
    else:
        endDate = datetime.strptime(endDate, "%Y-%m-%d").date()


    # Calculate model for entire set of valid data
    # al = AnalysisList(BIG_TICKERS, date(2021,11,1), date(2021,11,29))
    # c = al.num_correct_analyses()
    # v = al.num_valid_analyses()
    # p = 100.0 * c / v

    results = []    
    analysisList = AnalysisList(tickers, startDate, endDate)

    for a in analysisList:
        results.append({
            "ticker": a.ticker,
            "date": a.test_date,
            "sentiment": a.sentiment,
            "isBuy": a.is_buy(),
            "isCorrect": a.is_correct(),
            "today_open": a.open,
            "today_close": a.close,
            "is_market_closed": a.is_market_closed(),
            "num_tweet_today": len(a.tweets)

        })

    context = {
        'results' : results, 
        'tickers': tickers,
        'num_correct': analysisList.num_correct_analyses(),
        'num_valid': analysisList.num_valid_analyses(),
        'correct_percentage': 100.0 * analysisList.num_correct_analyses()/analysisList.num_valid_analyses()
    }

    return render(request, 'evaluateModel.html', context)

def textSentimentSpeedTest(request):
    tweets = Tweet.objects.filter(ticker = "TSLA").order_by("id")[:10]

    start = time.time()

    for tweet in tweets:
        #print(tweet.text)
        #textSentiment(tweet.text)
        tweet.calcSentiment()

    end = time.time()

    return HttpResponse(f"Total Time: {str(end - start)}")
