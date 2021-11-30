from .models import Tweet, StockPrice

from datetime import timedelta

class AnalysisResult:
    
    def __init__(self, ticker, test_date):
        self.ticker = ticker
        self.test_date = test_date

        next_date = self.test_date + timedelta(days=1)
        self.tweets = Tweet.objects.filter(ticker = ticker).filter(created_at__date=self.test_date)
        # DOES TWEETS NEED TO BE CONVERTED TO A LIST?
        self.sentiment, _, _, _, _, _, _ = Tweet.calcSentimentOfTweetSet(self.tweets)
        self.open, self.close = StockPrice.getStockPrices(ticker, self.test_date)
        

    def is_market_closed(self):
        return self.open == -1 or self.close == -1

    def is_valid_analysis(self):
        return (
            len(self.tweets) > 0 
            and not self.is_market_closed()
        )

    def is_buy(self):
        return self.sentiment >= 0
    
    def is_correct(self):
        return (
            self.is_buy() and self.close >= self.open
            or not self.is_buy() and self.close < self.open
        )



class AnalysisList:
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

        days = (self.end_date - self.start_date).days + 1 #Add one so we're inclusive


        dates = [self.start_date + timedelta(days=d) for d in range(days)]

        self.analysis_list = []

        for ticker in tickers:
            for d in dates:
                self.analysis_list.append(AnalysisResult(ticker, d))

    def __iter__(self):
        return iter(self.analysis_list)

    
    def num_correct_analyses(self):
        correct_analyses = [a for a in self.analysis_list if a.is_valid_analysis() and a.is_correct()]

        return len(correct_analyses)
        
    def num_valid_analyses(self):
        valid_analyses = [a for a in self.analysis_list if a.is_valid_analysis()]
        
        return len(valid_analyses)
