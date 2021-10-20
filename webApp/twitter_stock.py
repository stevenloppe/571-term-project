from twitter import *
from datetime import datetime

class Tweet:
    def __init__(self, id, created_at, text, ticker, is_retweet):
        self.id = id
        self.created_at = created_at
        self.text = text
        self.ticker = ticker

        self.is_retweet = is_retweet

        # We might want to know when the info about a tweet was gathered because that will affect the retweet and follower counts
        self.fetched_at = datetime.now() 
        



class TwitterStock:
    
    def __init__(self):
        API_KEY = "Fy2ufDgWjZppcZcOIE4UyW15J"
        API_KEY_SECRET = "NXsPLbdP5TDx2PwYcUHHTpB1liyhwtSMTGR6VNVq16b9YstmtD"
        BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGbBUgEAAAAAtGrIWJwh8C9Y34dWbtKivErpsYw%3D2QwSepZaFKmAaFiwgLJjGokfsErKCavVmATg5JBEllpDIooRy9"
        ACCESS_TOKEN = "1445439605847642113-v2YUfIiTQVAuS4nvZLHI7ysd7cTl0d"
        ACCESS_TOKEN_SECRET = "52AtMUpzJZlkNvTarMKh9xBkAPcPZzRAcL4IRk02CKlGI"

        self.twitter = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET))


    def getTweetsForStock(self, ticker, filter_retweets=True, filter_links=True):
        # TODO: Remove tweets that reference multiple stock tickers
        # TODO: Update Readme to include all install instructions necessary to get twitter working
        # TODO: Extract extra metadata info into its own object (retweets, date retrieved, author, author followers)

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

        return statuses


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
            tweet = Tweet(s["id"], s["created_at"], s["full_text"], ticker, "retweeted_status" in s)
            result.append(tweet)

        return result
            
            

        

