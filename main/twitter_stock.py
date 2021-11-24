from twitter import *
from datetime import date, datetime, timedelta, timezone
import emoji
import regex
import pytz
import yfinance as yf

from main.EmojiTranslation import emojiSentiment
from main.TextSentiment import textSentiment

from django.db.models import Max

#from main.models import Tweet as TweetModel
#from main.models import Author as AuthorModel
#from main.models import TweetSymbols as TweetSymbolsModel

# class Author:
#     def __init__(self, id, name, followers_count):
#         self.id  = id
#         self.name = name
#         self.followers_count = followers_count

#         # https://stackoverflow.com/a/7711869
#         #self.created_at = datetime.fromisoformat(datetime.strftime(datetime.strptime(created_at,'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S'))


# class Tweet:
#     def __init__(self, *args):
#         if(len(args) == 1):
#             tweet = args[0]
#             author = Author(tweet.author.id, tweet.author.name, tweet.author.followers_count)
#             id = tweet.id
#             created_at = tweet.created_at
#             text = tweet.text
#             ticker = tweet.ticker
#             is_retweet = tweet.is_retweet
#             favorite_count = tweet.favorite_count
#             retweet_count = tweet.retweet_count
#             symbols = tweet.symbols
#         else:
#             id, created_at, text, ticker, is_retweet, favorite_count, retweet_count, author, symbols = args

#         self.id = id

#         if(type(created_at) is datetime):
#             self.created_at = created_at
#         else:
#             # https://stackoverflow.com/a/7711869
#             created_at = datetime.fromisoformat(datetime.strftime(datetime.strptime(created_at,'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S'))
#             self.created_at = datetime(year=created_at.year, month=created_at.month, day=created_at.day, hour=created_at.hour, minute=created_at.minute, second=created_at.second, microsecond=created_at.microsecond, tzinfo=timezone.utc)

#         self.text = text
#         self.ticker = ticker
#         self.is_retweet = is_retweet
#         self.favorite_count = favorite_count
#         self.retweet_count = retweet_count
        
        
#         # BUG: Twitter fails to identify stock symbols when they end with ellipses, like so:
#         #   '@Kristennetten There’s a chance that by then I’m retired thanks to $TSLA… making it possible to do things for the less fortunate…'    
#         #   '@Keubiko Example: there’s a guy who named himself deep value on Twitter who’s bullish on $tsla…'
#         # 
#         # TODO: Perhaps we should manually extract these? Is this easy? I think 
#         #   it would require knowing all stock symbols else we risk filtering 
#         #   out tweets that contain strings like "$cash money$" because we 
#         #   would assume that "$cash" was a stock symbol even though it isn't.
        
#         # These are the symbols that twitter says are in the tweet
#         self.symbols = symbols

#         # We might want to know when the info about a tweet was gathered because that will affect the retweet and follower counts
#         self.fetched_at = datetime.now(timezone.utc)

#         self.author = author

#         self.emojis = self.get_emojis(self.text)
#         self.text_without_emojis = emoji.replace_emoji(text, "")
#         self.emojis_len = len(self.emojis)
#         self.text_len = len(self.text_without_emojis)
#         self.emoji_sentiment = emojiSentiment(self.emojis)
#         self.text_sentiment = textSentiment(self.text_without_emojis)


#     # Extract Emojis
#     # https://stackoverflow.com/a/49242754
#     def get_emojis(self, text):

#         emoji_list = []
#         data = regex.findall(r'\X', text)
#         for word in data:
#             if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
#                 emoji_list.append(word)
        
#         return emoji_list

        



class TwitterStock:
    
    def __init__(self):
        API_KEY = "Fy2ufDgWjZppcZcOIE4UyW15J"
        API_KEY_SECRET = "NXsPLbdP5TDx2PwYcUHHTpB1liyhwtSMTGR6VNVq16b9YstmtD"
        BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGbBUgEAAAAAtGrIWJwh8C9Y34dWbtKivErpsYw%3D2QwSepZaFKmAaFiwgLJjGokfsErKCavVmATg5JBEllpDIooRy9"
        ACCESS_TOKEN = "1445439605847642113-v2YUfIiTQVAuS4nvZLHI7ysd7cTl0d"
        ACCESS_TOKEN_SECRET = "52AtMUpzJZlkNvTarMKh9xBkAPcPZzRAcL4IRk02CKlGI"

        self.twitter = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET))

        

    def getStockPrices(self, ticker, start):
        startDate = start - timedelta(days=2)
        end = start + timedelta(days=2)
        ticker = yf.Ticker(ticker)
        hist = ticker.history(start=startDate, end=end)

        startTest = start
        endTest = start + timedelta(days=1)

        histTest = ticker.history(start=startTest, end=endTest)
        
        for index, row in hist.iterrows():
            if(index.year == start.year and index.month == start.month and index.day == start.day):
                return row.Open, row.Close


        # No market data, was probably closed
        return -1, -1
        

    # def fetchTweetsFromApi(self, ticker, filter_retweets=True, filter_links=True):
    #     # Fetches as many tweets from the Twitter api that are not already stored 
    #     # in the database as we can


    #     # Remove retweets
    #     retweets = "-filter:retweets" if filter_retweets else ""
        
    #     # Remove tweets with links in them
    #     links = "-filter:links" if filter_links else ""

    #     args = {
    #         "q"           : "${0} {1} {2}".format(ticker,retweets,links),
    #         # This is the max we're allowed to get
    #         "count"       : 100, 
    #         # If we're only analysing english then we should only get english tweets
    #         "lang"        :"en", 
    #         # By default the api will return a mix of recent and popular tweets, we want the most recent
    #         "result_type" : "recent",
    #         # By default this api version will only return 140 characters for a tweet, if the tweet is more then it will be truncated.
    #         "tweet_mode"  : "extended" 
    #     }

    #     # highest id stored in the database for the specified ticker
    #     tweet_with_highest_id = TweetModel.objects.filter(ticker = ticker).order_by('-id').first()
        
    #     # We don't want tweets that are older than this since we already have them
    #     if(tweet_with_highest_id is not None):
    #         args["since_id"] = tweet_with_highest_id.id

        
    #     result = self.twitter.search.tweets(**args)
        
    #     statuses = [] + self.extractTweets(result["statuses"], ticker)
        
    #     api_requests = 1


    #     print("API Rate Limit Remaining: " + str(result.rate_limit_remaining))

    #     if result.rate_limit_remaining <= 0:
    #         # Stop if we've hit our api limit
    #         return statuses


    #     if len(statuses) > 0:
    #         oldest_tweet_datetime = min(statuses, key=lambda s: s.created_at).created_at
    #     else:
    #         oldest_tweet_datetime = None

    #     ## as long as the last api request returned some results AND
    #     #  we haven't hit the hardcoded api request limit, keep getting results 
    #     while (len(result["statuses"]) > 0 and api_requests < 50):
    #         args["max_id"] = self.min_id(statuses) - 1
            
    #         result = self.twitter.search.tweets(**args)
            
    #         statuses += self.extractTweets(result["statuses"], ticker)
            
    #         api_requests += 1
        

    #     # Filter any tweets with more than 1 stock symbol in them
    #     statuses1 = [s for s in statuses if len(s.symbols) <= 1]

    #     return statuses1

    

    # def getTweetsForStock(self, ticker, filter_retweets=True, filter_links=True):
    #     #tweets = self.fetchTweetsFromApi(ticker, filter_retweets, filter_links)
    #     tweets = TweetModel.fetchTweetsFromApi(ticker, filter_retweets, filter_links)

    #     # Store these tweets into the database.
    #     self.saveTweetsToDatabase(tweets);

    #     # Fetch results from database
    #     results = TweetModel.objects.filter(ticker = ticker).order_by("-id")

    #     # Remove any tweets older than 24 hours
    #     now = datetime.now(timezone.utc)
    #     yesterday = now - timedelta(days=1)
    #     results1 = [s for s in results if s.created_at > yesterday]

    #     return results1

    # def saveTweetsToDatabase(self, tweets):
    #     for t in tweets:
    #         tm = TweetModel()
    #         tm.id = t.id
    #         tm.text = t.text
    #         tm.created_at = t.created_at
    #         tm.ticker = t.ticker
    #         tm.is_retweet = t.is_retweet
    #         tm.favorite_count = t.favorite_count
    #         tm.retweet_count = t.retweet_count
    #         tm.fetched_at = t.fetched_at
            
    #         authorExists = AuthorModel.objects.filter(id = t.author.id).count() >= 1

    #         if authorExists:
    #             tm.author = AuthorModel.objects.get(id=t.author.id)
    #         else:
    #             am = AuthorModel()
    #             am.id = t.author.id
    #             am.name = t.author.name
    #             am.followers_count = t.author.followers_count
    #             tm.author = am
    #             am.save()

    #         tm.save()

    #         for s in t.symbols:
    #             sm = TweetSymbolsModel()
    #             sm.symbol = s
    #             sm.tweet = tm
    #             sm.save()


    # def updateHistoricalDatabase(self):
    #     # This is a list of the 100 biggest stocks according to:
    #     # https://companiesmarketcap.com/
    #     big_tickers = ["MSFT","AAPL","2222.SR","GOOG","AMZN","TSLA","FB","NVDA","BRK-A","TSM","TCEHY","JPM","V","BABA","UNH","JNJ","WMT","LVMUY","005930.KS","HD","BAC","NSRGY","ASML","600519.SS","PG","RHHBY","MA","ADBE","DIS","CRM","NFLX","XOM","NKE","OR.PA","PFE","NVO","ORCL","LLY","TM","CMCSA","TMO","KO","CSCO","1398.HK","300750.SZ","PYPL","AVGO","ACN","RELIANCE.NS","PEP","ABT","COST","CVX","VZ","DHR","MPNGF","INTC","MRK","ABBV","3968.HK","WFC","SHOP","AZN","SE","MCD","QCOM","NVS","UPS","AMD","TXN","MS","RYDAF","SAP","T","TCS.NS","PRX.VI","INTU","LIN","HESAF","CICHY","NEE","MDT","LOW","HON","KYCCF","SONY","ACGBY","UNP","SCHW","RY","TMUS","VOW3.DE","CDI.PA","BLK","PM","002594.SZ","CBA.AX","PNGAY","AMAT","AXP"]

    #     for big_t in big_tickers:
    #         tweets = self.fetchTweetsFromApi(big_t)
    #         self.saveTweetsToDatabase(tweets)
    #         print("Saved: " + big_t)



            

        
            


            


    # Helper functions

    # def extract_id(self, e):
    #     return e.id

    # def min_id(self, statuses):
    #     min_id = statuses[0].id

    #     for status in statuses:
    #         if status.id < min_id:
    #             min_id = status.id

    #     return min_id

    # def extractTweets(self, statuses, ticker):
    #     result = []
    #     for s in statuses:
    #         author = Author(s["user"]["id"], s["user"]["name"], s["user"]["followers_count"])
    #         symbols = [symbol["text"] for symbol in s["entities"]["symbols"]]
    #         tweet = Tweet(s["id"], s["created_at"], s["full_text"], ticker, "retweeted_status" in s, s["favorite_count"], s["retweet_count"], author, symbols)
    #         result.append(tweet)

    #     return result
