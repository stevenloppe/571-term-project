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


OPTIONAL TODO:
 - Only update stock sentiment information if the information if out of date
 - Add a loading circle or something while waiting for sentiment calculation
 - Finish frontend
     - Add a table for 'most recently searched for sentiments' to home page
     - Add an About section to the home page
     - everything in stockdetails.html