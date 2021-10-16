from django.shortcuts import render
from django.http import HttpResponse
from twitter import *


def index(request):
    return HttpResponse("Hello, world.")


def twittertest(request):
    API_KEY = "Fy2ufDgWjZppcZcOIE4UyW15J"
    API_KEY_SECRET = "NXsPLbdP5TDx2PwYcUHHTpB1liyhwtSMTGR6VNVq16b9YstmtD"
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGbBUgEAAAAAtGrIWJwh8C9Y34dWbtKivErpsYw%3D2QwSepZaFKmAaFiwgLJjGokfsErKCavVmATg5JBEllpDIooRy9"
    ACCESS_TOKEN = "1445439605847642113-v2YUfIiTQVAuS4nvZLHI7ysd7cTl0d"
    ACCESS_TOKEN_SECRET = "52AtMUpzJZlkNvTarMKh9xBkAPcPZzRAcL4IRk02CKlGI"

    t = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET))
    
    statuses = []
    count = 0

    result = t.search.tweets(q="$TSLA -filter:retweets -filter:links", count=100, lang="en", result_type="recent", tweet_mode="extended")

    while (len(result["statuses"]) > 0 and count < 5):
        count += 1
        statuses = statuses + result["statuses"]
        next_max_id = min_id(result["statuses"]) - 1
        result = t.search.tweets(q="$TSLA -filter:retweets -filter:links", count=100, lang="en", result_type="recent", tweet_mode="extended", max_id = next_max_id)

    statuses.sort(key=thing)
    statuses.reverse()

    responseText = """<table border=1>
    <thead>
        <tr>
            <th>#</th>
            <!--<th>Id</th>-->
            <th>Created</th>
            <th>Is Retweet</th>
            <th>Truncated</th>
            <th>Tweet</th>
        </tr>
    </thead>
    <tbody>"""

    status_count = 0
    for status in statuses:
        status_count += 1
        s = """
            <tr>
                <td>{status_count}</td>
                <!--<td>{id}</td>-->
                <td>{created_at}</td>
                <td>{is_retweet}</td>
                <td>{is_truncated}</td>
                <td>{text}</td>
            </tr>
        """
        responseText += s.format(status_count=status_count, id=status["id"], created_at=status["created_at"], text=status["full_text"], is_retweet="retweeted_status" in status, is_truncated=status["truncated"])

    responseText += "</tbody></table>"
    return HttpResponse(responseText)


def thing (e):
    return e["id"]

def min_id(statuses):
    min_id = statuses[0]["id"]

    for status in statuses:
        if status["id"] < min_id:
            min_id = status["id"]

    return min_id
