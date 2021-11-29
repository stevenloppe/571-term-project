from twitter import *
from datetime import date, datetime, timedelta, timezone
import emoji
import regex
import pytz
import yfinance as yf
import stockquotes

from main.EmojiTranslation import emojiSentiment
from main.TextSentiment import textSentiment

from django.db.models import Max



class TwitterStock:
    
    def __init__(self):
        API_KEY = "Fy2ufDgWjZppcZcOIE4UyW15J"
        API_KEY_SECRET = "NXsPLbdP5TDx2PwYcUHHTpB1liyhwtSMTGR6VNVq16b9YstmtD"
        BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGbBUgEAAAAAtGrIWJwh8C9Y34dWbtKivErpsYw%3D2QwSepZaFKmAaFiwgLJjGokfsErKCavVmATg5JBEllpDIooRy9"
        ACCESS_TOKEN = "1445439605847642113-v2YUfIiTQVAuS4nvZLHI7ysd7cTl0d"
        ACCESS_TOKEN_SECRET = "52AtMUpzJZlkNvTarMKh9xBkAPcPZzRAcL4IRk02CKlGI"

        self.twitter = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET))




        
