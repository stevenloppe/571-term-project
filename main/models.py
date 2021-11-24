from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone
import emoji
import regex
from django.contrib import admin
import time

from main import EmojiTranslation, TextSentiment
from main import twitter_stock



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

    # # https://stackoverflow.com/a/843740

    # # This is a class method that takes the result of the twitter api 
    # # and extracts the relevant values and returns an Author model
    # @classmethod
    # def getOrCreate(cls, status):
    #     return cls(
    #         id=status["user"]["id"], 
    #         name = status["user"]["name"], 
    #         followers_count = status["user"]["followers_count"]
    #     )


class Tweet(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=1024) # Greater than we should need
    created_at = models.DateTimeField()
    ticker = models.CharField(max_length=255)
    is_retweet = models.BooleanField()
    retweet_count = models.IntegerField()
    fetched_at = models.DateTimeField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    sentiment = models.FloatField(default = -2) #Default value is an invalid value
    sentiment_version = models.IntegerField(default=0)

    # We need to pre-calcuate the sentiment of each tweet since it takes too long to do on the fly.
    # If we ever update our analysis the precalculated sentiments would become invalid so we have
    # A version number on each tweet to tell us which version of the analysis we have.
    # This global variable is what we will increment if we change our analysis.
    CURRENT_SENTIMENT_VERSION = 1

    # Extract Emojis
    # https://stackoverflow.com/a/49242754
    def get_emojis(self, text):

        emoji_list = []
        data = regex.findall(r'\X', text)
        for word in data:
            if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
                emoji_list.append(word)
        
        return emoji_list

    def getSentimentAndUpdate(self):
        if self.sentiment_version < Tweet.CURRENT_SENTIMENT_VERSION:
            self.calcAndSaveSentiment()
        
        return self.sentiment

    def calcSentiment(self):
        emojis = self.get_emojis(self.text)
        text_without_emojis = emoji.replace_emoji(self.text, "")
        emojis_len = len(emojis)
        text_len = len(text_without_emojis)
        emoji_sentiment = EmojiTranslation.emojiSentiment(emojis)
        text_sentiment = TextSentiment.textSentiment(text_without_emojis)
        
        # Multiplying emoji sentiment weight by 8 so that 1 emoji = 8 characters in text
        new_emojis_len = emojis_len * 8
        textWeight = text_len / (text_len + new_emojis_len)
        emojiWeight = (new_emojis_len / (text_len + new_emojis_len))

        sentiment = (emoji_sentiment*2-1)*emojiWeight + (text_sentiment)*textWeight

        return sentiment

    def calcAndSaveSentiment(self):
        self.sentiment = self.calcSentiment()
        self.sentiment_version = Tweet.CURRENT_SENTIMENT_VERSION
        self.save()


###  Class Methods ###

    # @classmethod
    # def create(cls, status, author, ticker):
    #     symbols = [symbol["text"] for symbol in status["entities"]["symbols"]]

    #     created_at = datetime.fromisoformat(datetime.strftime(datetime.strptime(symbol["created_at"],'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S'))
    #     created_at = datetime(year=created_at.year, month=created_at.month, day=created_at.day, hour=created_at.hour, minute=created_at.minute, second=created_at.second, microsecond=created_at.microsecond, tzinfo=timezone.utc)

    #     return cls(
    #         id = status["id"], 
    #         text = status["full_text"], 
    #         created_at = created_at, 
    #         ticker = ticker, 
    #         is_retweet = "retweeted_status" in status, 
    #         retweet_count = status["retweet_count"], 
    #         fetched_at = datetime.now(timezone.utc), 
    #         author = author, 
    #         sentiment = -2, 
    #         sentiment_version = 0
    #    )

    @classmethod
    def fetchTweetsFromApi(cls, ticker, filter_retweets=True, filter_links=True):
        # Fetches as many tweets from the Twitter api that are not already stored 
        # in the database as we can


        # Remove retweets
        retweets = "-filter:retweets" if filter_retweets else ""
        
        # Remove tweets with links in them
        links = "-filter:links" if filter_links else ""

        args = {
            "q"           : "${0} {1} {2}".format(ticker,retweets,links),
            # This is the max we're allowed to get
            "count"       : 100, 
            # If we're only analysing english then we should only get english tweets
            "lang"        :"en", 
            # By default the api will return a mix of recent and popular tweets, we want the most recent
            "result_type" : "recent",
            # By default this api version will only return 140 characters for a tweet, if the tweet is more then it will be truncated.
            "tweet_mode"  : "extended" 
        }

        # highest id stored in the database for the specified ticker
        tweet_with_highest_id = Tweet.objects.filter(ticker = ticker).order_by('-id').first()
        
        # We don't want tweets that are older than this since we already have them
        if(tweet_with_highest_id is not None):
            args["since_id"] = tweet_with_highest_id.id

        twitterStock = twitter_stock.TwitterStock()
        result = twitterStock.twitter.search.tweets(**args)
        
        statuses = [] + result["statuses"]
        
        api_requests = 1


        print("API Rate Limit Remaining: " + str(result.rate_limit_remaining))

        if result.rate_limit_remaining <= 0:
            # Stop if we've hit our api limit
            return statuses


        if len(statuses) > 0:
            oldest_tweet_datetime = min(statuses, key=lambda s: s["created_at"])["created_at"]
        else:
            oldest_tweet_datetime = None

        ## as long as the last api request returned some results AND
        #  we haven't hit the hardcoded api request limit, keep getting results 
        while (len(result["statuses"]) > 0 and api_requests < 50):
            args["max_id"] = min(statuses, key=lambda s: s["id"])["id"] - 1
            
            result = twitterStock.twitter.search.tweets(**args)
            
            statuses += result["statuses"]
            
            api_requests += 1
        

        # Filter any tweets with more than 1 stock symbol in them
        statuses1 = [s for s in statuses if len(s["entities"]["symbols"]) <= 1]

        return statuses1

    @classmethod
    def getTweetsForStock(cls, ticker, filter_retweets=True, filter_links=True):
        #tweets = self.fetchTweetsFromApi(ticker, filter_retweets, filter_links)
        statuses = cls.fetchTweetsFromApi(ticker, filter_retweets, filter_links)

        # Store these tweets into the database.
        cls.saveTweetsToDatabase(statuses, ticker);

        # Fetch results from database
        results = Tweet.objects.filter(ticker = ticker).order_by("-id")

        # Remove any tweets older than 24 hours
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        results1 = [s for s in results if s.created_at > yesterday]

        return results1

    @classmethod
    def saveTweetsToDatabase(cls, statuses, ticker):
        for s in statuses:
            created_at = datetime.fromisoformat(datetime.strftime(datetime.strptime(s["created_at"],'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S'))
            created_at = datetime(year=created_at.year, month=created_at.month, day=created_at.day, hour=created_at.hour, minute=created_at.minute, second=created_at.second, microsecond=created_at.microsecond, tzinfo=timezone.utc)

            tweet = Tweet()
            tweet.id = s["id"]
            tweet.text = s["full_text"]
            tweet.created_at = created_at
            tweet.ticker = ticker
            tweet.is_retweet = "retweeted_status" in s
            tweet.retweet_count = s["retweet_count"]
            tweet.fetched_at = datetime.now(timezone.utc)
            tweet.sentiment = -2 # Do not calculate sentiment now. It is slow so we will do it later in batch
            tweet.sentiment_version = 0 # Since we didn't calculate sentiment the version is 0 so it will always be overwritten
            
            authorExists = Author.objects.filter(id = s["user"]["id"]).count() >= 1

            if authorExists:
                tweet.author = Author.objects.get(id=s["user"]["id"])
            else:
                author = Author()
                author.id = s["user"]["id"]
                author.name = s["user"]["name"]
                author.followers_count = s["user"]["followers_count"]
                tweet.author = author
                author.save()

            tweet.save()

            for sym in s["entities"]["symbols"]:
                TweetSymbol = TweetSymbols()
                TweetSymbol.symbol = sym["text"]
                TweetSymbol.tweet = tweet
                TweetSymbol.save()

    @classmethod
    def updateHistoricalDatabase(cls):
        # This is a list of the 100 biggest stocks according to:
        # https://companiesmarketcap.com/
        big_tickers = ["MSFT","AAPL","2222.SR","GOOG","AMZN","TSLA","FB","NVDA","BRK-A","TSM","TCEHY","JPM","V","BABA","UNH","JNJ","WMT","LVMUY","005930.KS","HD","BAC","NSRGY","ASML","600519.SS","PG","RHHBY","MA","ADBE","DIS","CRM","NFLX","XOM","NKE","OR.PA","PFE","NVO","ORCL","LLY","TM","CMCSA","TMO","KO","CSCO","1398.HK","300750.SZ","PYPL","AVGO","ACN","RELIANCE.NS","PEP","ABT","COST","CVX","VZ","DHR","MPNGF","INTC","MRK","ABBV","3968.HK","WFC","SHOP","AZN","SE","MCD","QCOM","NVS","UPS","AMD","TXN","MS","RYDAF","SAP","T","TCS.NS","PRX.VI","INTU","LIN","HESAF","CICHY","NEE","MDT","LOW","HON","KYCCF","SONY","ACGBY","UNP","SCHW","RY","TMUS","VOW3.DE","CDI.PA","BLK","PM","002594.SZ","CBA.AX","PNGAY","AMAT","AXP"]

        for big_t in big_tickers:
            tweets = cls.fetchTweetsFromApi(big_t)
            cls.saveTweetsToDatabase(tweets)
            print("Saved: " + big_t)
        
    @classmethod
    def calcSentimentOfTweetSet(cls, tweets):
        sentimentSum = 0
        numPositive = 0
        numNeutral = 0
        numNegative = 0

        for t in tweets:
            sentiment = t.getSentimentAndUpdate()
            sentimentSum += sentiment
            if sentiment < -0.25:
                numNegative += 1
            elif sentiment < 0.25:
                numNeutral += 1
            else:
                numPositive += 1

        sentimentScore = sentimentSum / len(tweets) 

        return (sentimentScore, numPositive, numNeutral, numNegative)

    @classmethod
    def updateSentimentForDatabaseTweets(cls):
        tweets = Tweet.objects.filter(sentiment_version__lt=Tweet.CURRENT_SENTIMENT_VERSION)[:100]
    
        while(len(tweets) > 0):
            for tweet in tweets:
                tweet.calcAndSaveSentiment()
            tweets = Tweet.objects.filter(sentiment_version__lt=Tweet.CURRENT_SENTIMENT_VERSION)[:100]

            count = Tweet.objects.filter(sentiment_version=Tweet.CURRENT_SENTIMENT_VERSION).count()
            total_count = Tweet.objects.count()
            print(f"Tweets with sentiment version {Tweet.CURRENT_SENTIMENT_VERSION}: {count}/{total_count}")
            time.sleep (10) # To give my CPU a rest
    


class TweetSymbols(models.Model):
    tweet = models.ForeignKey(Tweet, related_name="symbols", on_delete=models.CASCADE)
    symbol = models.CharField(max_length=255)


