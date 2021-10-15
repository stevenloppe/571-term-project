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

    result = t.search.tweets(q="$APPL -filter:retweets", count=100, lang="en", result_type="recent")

    while (len(result["statuses"]) > 0 and count < 5):
        # WARNING: this code currently returns the same tweets 5 times, I think.
        count += 1
        statuses = statuses + result["statuses"]
        next_max_id = result["search_metadata"]["max_id"] - 1
        result = t.search.tweets(q="$APPL -filter:retweets", count=100, lang="en", result_type="recent", max_id = next_max_id)

    statuses.sort(key=thing)

    responseText = """<table border=1>
    <thead>
        <tr>
            <th>Id</th>
            <th>Created</th>
            <th>Is Retweet</th>
            <th>Tweet</th>
        </tr>
    </thead>
    <tbody>"""

    for status in statuses:
        s = """
            <tr>
                <td>{id}</td>
                <td>{created_at}</td>
                <td>{is_retweet}</td>
                <td>{text}</td>
            </tr>
        """
        responseText += s.format(id=status["id"], created_at=status["created_at"], text=status["text"], is_retweet="retweeted_status" in status)

    responseText += "</tbody></table>"
    return HttpResponse(responseText)


def thing (e):
    return e["id"]