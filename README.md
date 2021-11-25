# 571-term-project
//testing


http://127.0.0.1:8000/admin/

Admin login information

Username: ```cpsc571project```

password: ```d?!q4k\>6)D2j^{C```



Emoji Sentiment Table from:
http://kt.ijs.si/data/Emoji_sentiment_ranking/about.html



Packages:

`pip install regex`
`pip install twitter`
`pip install yfinance`


# Setting up database for storing tweets from twitter

1. Create initial models
2. Run `python manage.py makemigrations main`
3. Run `python manage.py sqlmigrate main 0001`
4. Run `python manage.py migrate`


FRONTEND TODO:

index.html:
 - Everything
 - Add a table for 'most recently searched for sentiments'
 - Add an 'ABOUT' section

stockdetails.html:
 - Center sentimentscore text
 - Clean up numTweets display
 - Show last updated time in a more readable format and local time zone
 - Make it look good on smaller screens
