from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render
from .models import StockAnalysis

from twitter import *
from main.twitter_stock import TwitterStock

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


def twittertest(request):
    # use ticker symbol in "tick" url param or default to APPL
    ticker = request.GET["ticker"] if "ticker" in request.GET else "APPL"

    twitterStock = TwitterStock()
    statuses = twitterStock.getTweetsForStock(ticker)


    responseText = """<table border=1>
    <thead>
        <tr>
            <th>#</th>
            <!--<th>Id</th>-->
            <th>Created</th>
            <!--<th>Is Retweet</th>-->
            <th>Tweet</th>
        </tr>
    </thead>
    <tbody>"""

    status_count = 0
    for status in statuses:
        status_count += 1
        s = """
            <tr>
                <td>{status_count}</td>
                <!--<td>{id}</td>-->
                <td>{created_at}</td>
                <!--<td>{is_retweet}</td>-->
                <td>{text}</td>
            </tr>
        """
        responseText += s.format(status_count=status_count, id=status.id, created_at=status.created_at, text=status.text, is_retweet=status.is_retweet)

    responseText += "</tbody></table>"
    return HttpResponse(responseText)