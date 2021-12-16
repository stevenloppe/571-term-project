# 571-term-project

## Getting the application running

### Overview

Our appliation is a python web site using the Django framework. It runs on python 3.8 (and possibly others).

### Installing dependencies 

Note: if your python 3 installation is called `python3` then all references to the `python` command in this document should be replaced with `python3`. It also might be safer to use `pip3` whenever you need to use `pip`


If your python install doesn't have pip it will need to be installed. On a debian based machine the following command will likely work: `sudo apt install python-pip`.
Note: there is a chance the package will be called `python3-pip`


Our application requires the following packages be installed via pip as seen below:

Packages:
- `python -m pip install Django`
- `pip install emoji`
- `pip install regex`
- `pip install twitter`
- `pip install lxml`
- `pip install beautifulsoup4`
- `pip install stanza`

### Installing and running

Since this code will be submitted to a dropbox I will assume the marker already has a copy of it.

Copy the code to the server it is being executed on and navigate to the main folder (the one containing manage.py)

To start the server execute: `python manage.py runserver` This will run the application on localhost at port 8000 by default.


## Overview of the pages that exist, where they are, what they do and how to use them

### main page (/)

The main page contains a form to enter a stock ticker and see details about it. The table below shows recent searches.

### stock details page (/<TICKER>)

The stock details page is where you are taken when you search for a ticker from the main page. This page analyses the sentiment for tweets from the past 24 hours and provides a breakdown of positive, neutral, and negative tweets

### evaluate model page (/evaluateModel)

The evaluate model page will test our model against the historical stock prices for the relevant day to see if our sentiment prediction was correct. Our model is considered correct if the price went up and our sentiment was positive, or if the price went down and our sentiment was negative. 

Each row is for a specific stock ticker for a specific day and a row is only considered "valid" (for testing purposes) if the stock market was open on that day AND we have some tweets for that stock/date combo. 

This table will show all of the tested stock/date's combos even if they are invalid for testing purposes. However the analysis at the top of the page show the ratio of correct predictions will filter out any invalid tests. So this ratio is showing: <number_of_correct_and_valid_tests>/<number_of_valid_tests>

#### Parameters

This page has a number of url parameters that can be used to alter its behaviour

**tickers** : This param is a comma separated list of stock tickers to test for. Example: /evaluateModel?tickers=AAPL,MSFT
    This param also has a magic string "\_\_ALL\_\_" which will use the complete list of stock tickers that we have gathered data for

**startDate**: This is the start of the date range to test against. We only have data going back to about November 15th (some stocks have data back that far, some don't)

**endDate**: This is the end of the date range to test against.

Example full query: /evaluateModel?tickers=\_\_ALL\_\_&startDate=2021-11-15&endDate=2021-12-10

**Warning**: Increasing the date range to test against will make the response take longer! The console will output the stock ticker currently being analysed so you can get an idea of how fast it is moving. Executing the above example query takes about 5 minutes to respond on my machine.


## Batch urls

Since our pages are already relatively slow we preprocess as much data as we can into our database, these preprocessing operations can be accessed via the following urls:

### update historical database (/updateHistoricalDatabase)

This url will hit the twitter api and retrieve any tweets that we don't already have. We are rate-limited to 180 requests per 15 minutes so it is likely this url will hit that limit and need to be re-run later.

### Update sentiment for stored tweets (/updateSentimentForStoredTweets)

This url will go through our database of tweets and determine the sentiment for any tweets that haven't already been determined. This operation is slow and CPU intensive! It is recommended that you run this after updating the historical database to give the api rate limit time to reset (then run them both again after)

### Update historical stock prices (/updateHistoricalStockPrices)

This url will update our database of historical stock prices, it doesn't take as long as the others and doesn't have any rate limitations. 

### Recommended execution order:

1. /updateHistoricalDatabase
2. /updateSentimentForStoredTweets
3. /updateHistoricalStockPrices
4. Repeat steps 1 and 2 until step 1 no longer hits the api limit


## Accessing the admin interface

The admin interface (provided by Django) can be accessed at /admin with the following credentials

Username: ```cpsc571project```
password: ```d?!q4k\>6)D2j^{C```

The admin interface likely won't be needed.





