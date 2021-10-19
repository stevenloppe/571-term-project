from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

from twitter import *
from webApp.twitter_stock import TwitterStock




TEMPLATE_DIRS = (
    'os.path.join(BASE_DIR, "templates"),'
)

def index(request):
    return render(request,"index.html")


def twittertest(request):
    # use ticker symbol in "tick" url param or default to APPL
    ticker = request.GET["ticker"] if "ticker" in request.GET else "APPL"

    twitterStock = TwitterStock()
    statuses = twitterStock.getTweetsForStock(ticker)


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




