from twitter import *

class TwitterStock:
    
    def __init__(self):
        API_KEY = "Fy2ufDgWjZppcZcOIE4UyW15J"
        API_KEY_SECRET = "NXsPLbdP5TDx2PwYcUHHTpB1liyhwtSMTGR6VNVq16b9YstmtD"
        BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGbBUgEAAAAAtGrIWJwh8C9Y34dWbtKivErpsYw%3D2QwSepZaFKmAaFiwgLJjGokfsErKCavVmATg5JBEllpDIooRy9"
        ACCESS_TOKEN = "1445439605847642113-v2YUfIiTQVAuS4nvZLHI7ysd7cTl0d"
        ACCESS_TOKEN_SECRET = "52AtMUpzJZlkNvTarMKh9xBkAPcPZzRAcL4IRk02CKlGI"

        self.twitter = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET))


    def getTweetsForStock(self, ticker, filter_retweets=True, filter_links=True):
        
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
        statuses = [] + result["statuses"]
        api_requests = 1

        ## as long as the last api request returned some results AND
        #  we haven't hit the hardcoded api request limit, keep getting results
        while (len(result["statuses"]) > 0 and api_requests < 5):
            args["max_id"] = self.min_id(statuses) - 1
            result = self.twitter.search.tweets(**args)
            statuses += result["statuses"]
            api_requests += 1
        
        # Sorting by ID and reversing gives us the newest tweets first
        statuses.sort(key=self.extract_id)
        statuses.reverse()

        return statuses


    # Helper functions

    def extract_id(self, e):
        return e["id"]

    def min_id(self, statuses):
        min_id = statuses[0]["id"]

        for status in statuses:
            if status["id"] < min_id:
                min_id = status["id"]

        return min_id

        

