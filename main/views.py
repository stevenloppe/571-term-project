from datetime import datetime
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

    twitterStock = TwitterStock()
    tweets = twitterStock.getTweetsForStock(sa_stockTicker)
    tweets = analyseTweets(tweets)

    try:
        stockAnalysis = StockAnalysis.objects.get(stockTicker = sa_stockTicker)
    except:
        stockAnalysis = StockAnalysis()

    stockAnalysis.stockTicker = sa_stockTicker
    stockAnalysis.lastUpdated = datetime.utcnow()
    stockAnalysis.numTweets = len(tweets)
    
    emojiPositiveSentimentSum = 0
    for t in tweets:
        emojiPositiveSentimentSum += t.emoji_sentiment

    # positiveSentiment and negativeSentiment are integers, not floats so for now multiplying them by 100 so it isn't saved as 0
    stockAnalysis.positiveSentiment = (emojiPositiveSentimentSum / len(tweets) ) * 100

    # TODO: Need to determine both positive and negative sentiment for emojis
    stockAnalysis.negativeSentiment = (emojiPositiveSentimentSum / len(tweets) ) * 100

    print("Before PSentiment: ",stockAnalysis.positiveSentiment)
    print("Before NSentiment: ",stockAnalysis.negativeSentiment)

    stockAnalysis.save()

    stockAnalysis2 = StockAnalysis.objects.get(stockTicker = sa_stockTicker)
    print("After PSentiment: ",stockAnalysis2.positiveSentiment)
    print("After NSentiment: ",stockAnalysis2.negativeSentiment)

    #try:
    #    stock = get_object_or_404(StockAnalysis, stockTicker=sa_stockTicker)
    #except StockAnalysis.DoesNotExist:
        #TODO: Run the method to calcuate sentiment and add it to the database
    #    raise Http404("To be updated")
    #if (stock.is_outdated)
        #TODO: Run the method to calcuate sentiment and update the database
    return render(request, 'stockdetails.html', { 'stock' : stockAnalysis, 'tweets': tweets })


def updateHistoricalDatabase(request):
    twitter_stock = TwitterStock()
    twitter_stock.updateHistoricalDatabase()
    
    return HttpResponse("Finished")







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