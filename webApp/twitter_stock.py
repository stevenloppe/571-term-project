from twitter import *
from datetime import datetime

class Tweet:
    def __init__(self, id, created_at, text, ticker, is_retweet, retweet_count, author, symbols):
        self.id = id
        self.created_at = created_at
        self.text = text
        self.ticker = ticker
        self.is_retweet = is_retweet
        self.retweet_count = retweet_count
        
        
        # BUG: Twitter fails to identify stock symbols when they end with ellipses, like so:
        #   '@Kristennetten There’s a chance that by then I’m retired thanks to $TSLA… making it possible to do things for the less fortunate…'    
        #   '@Keubiko Example: there’s a guy who named himself deep value on Twitter who’s bullish on $tsla…'
        # 
        # TODO: Perhaps we should manually extract these? Is this easy? I think 
        #   it would require knowing all stock symbols else we risk filtering 
        #   out tweets that contain strings like "$cash money$" because we 
        #   would assume that "$cash" was a stock symbol even though it isn't.
        
        # These are the symbols that twitter says are in the tweet
        self.symbols = symbols

        # We might want to know when the info about a tweet was gathered because that will affect the retweet and follower counts
        self.fetched_at = datetime.now()

        self.author = author

class Author:
    def __init__(self, id, name, followers_count, created_at):
        self.id  = id
        self.name = name
        self.followers_count = followers_count
        self.created_at = created_at
        



class TwitterStock:
    
    def __init__(self):
        API_KEY = "Fy2ufDgWjZppcZcOIE4UyW15J"
        API_KEY_SECRET = "NXsPLbdP5TDx2PwYcUHHTpB1liyhwtSMTGR6VNVq16b9YstmtD"
        BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGbBUgEAAAAAtGrIWJwh8C9Y34dWbtKivErpsYw%3D2QwSepZaFKmAaFiwgLJjGokfsErKCavVmATg5JBEllpDIooRy9"
        ACCESS_TOKEN = "1445439605847642113-v2YUfIiTQVAuS4nvZLHI7ysd7cTl0d"
        ACCESS_TOKEN_SECRET = "52AtMUpzJZlkNvTarMKh9xBkAPcPZzRAcL4IRk02CKlGI"

        self.twitter = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET))


    def getTweetsForStock(self, ticker, filter_retweets=True, filter_links=True):
        # TODO: Update Readme to include all install instructions necessary to get twitter working
        
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

        result = self.twitter.search.tweets(**args)
        statuses = [] + self.extractTweets(result["statuses"], ticker)
        api_requests = 1

        ## as long as the last api request returned some results AND
        #  we haven't hit the hardcoded api request limit, keep getting results
        while (len(result["statuses"]) > 0 and api_requests < 5):
            args["max_id"] = self.min_id(statuses) - 1
            result = self.twitter.search.tweets(**args)
            statuses += self.extractTweets(result["statuses"], ticker)
            api_requests += 1
        
        # Sorting by ID and reversing gives us the newest tweets first
        statuses.sort(key=self.extract_id)
        statuses.reverse()

        # Filter any tweets with more than 1 stock symbol in them
        statuses1 = [s for s in statuses if len(s.symbols) <= 1]

        return statuses1


    # Helper functions

    def extract_id(self, e):
        return e.id

    def min_id(self, statuses):
        min_id = statuses[0].id

        for status in statuses:
            if status.id < min_id:
                min_id = status.id

        return min_id

    def extractTweets(self, statuses, ticker):
        result = []
        for s in statuses:
            author = Author(s["user"]["id"], s["user"]["name"], s["user"]["followers_count"], s["user"]["created_at"])
            symbols = [symbol["text"] for symbol in s["entities"]["symbols"]]
            tweet = Tweet(s["id"], s["created_at"], s["full_text"], ticker, "retweeted_status" in s, s["retweet_count"], author, symbols)
            result.append(tweet)

        return result
            
            

        

