const spinnerBox = document.getElementById('spinner-box');
const dataBox = document.getElementById('data-box');

var ticker = document.getElementById("tickerjs").value;


window.twttr = (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0],
      t = window.twttr || {};
    if (d.getElementById(id)) return t;
    js = d.createElement(s);
    js.id = id;
    js.src = "https://platform.twitter.com/widgets.js";
    fjs.parentNode.insertBefore(js, fjs);
  
    t._e = [];
    t.ready = function(f) {
      t._e.push(f);
    };
  
    return t;
  }(document, "script", "twitter-wjs"));


$.ajax({
    type: 'GET',
    url: 'stockAnalysis_json',
    data: {"stockTicker":ticker},
    dataType: 'json',
    success: function(response) {
        console.log('response',response);
        console.log('success');
        spinnerBox.classList.add('invisible');
        dataBox.classList.remove('invisible');

        const stockAnalysis = JSON.parse(response);
        document.getElementById("stockTicker").innerHTML = stockAnalysis.stockTicker;
        document.getElementById("lastUpdated").innerHTML = stockAnalysis.lastUpdated;
        document.getElementById('sentimentScore').innerHTML = parseInt(stockAnalysis.sentimentScore);
        document.getElementById('numTweets').innerHTML += stockAnalysis.numTweets;
        document.getElementById('numPositiveTweets').innerHTML += stockAnalysis.numPositiveTweets;
        document.getElementById('numNeutralTweets').innerHTML += stockAnalysis.numNeutralTweets;
        document.getElementById('numNegativeTweets').innerHTML += stockAnalysis.numNegativeTweets;

        const sentimentDescription = document.getElementById('sentimentDescription');
        const sentiment = parseInt(stockAnalysis.sentimentScore);
        if (sentiment > 50){
            sentimentDescription.innerHTML += "Very Positive";
        }
        else if (sentiment > 15) {
            sentimentDescription.innerHTML += "Positive";
        }
        else if (sentiment > -15) {
            sentimentDescription.innerHTML += "Neutral";
        }
        else if (sentiment > -50) {
            sentimentDescription.innerHTML += "Negative";
        }
        else {
            sentimentDescription.innerHTML += "Very Negative";
        }

        const ratingPointer = document.getElementById('rating-pointer');
        const pointerOffset = 196 + (parseInt(stockAnalysis.sentimentScore) * 2); // 80 pixels per 0.5 increment
        ratingPointer.setAttribute('style','padding-left:'+pointerOffset+'px; margin-bottom: -0.8em;');
        //const ratingText = document.getElementById('sentimentScore');
        //ratingText.setAttribute('style','padding-left:'+Number(pointerOffset-16)+'px;');
        console.log('pointerOffset',pointerOffset);

        // Update bar lengths to match their ratios        
        if (stockAnalysis.numTweets > 1) {
            console.log('Attempting to update bar ratios');

            const posTweetsBar = document.getElementById('numPositiveTweets-bar');
            const posBarRatio = parseInt(stockAnalysis.numPositiveTweets)/parseInt(stockAnalysis.numTweets)*100;
            posTweetsBar.setAttribute('aria-valuenow',posBarRatio);
            posTweetsBar.setAttribute('style','width:'+Number(posBarRatio)+'%; background-color:#26bf2b;' );

            const neuTweetsBar = document.getElementById('numNeutralTweets-bar');
            const neuBarRatio = parseInt(stockAnalysis.numNeutralTweets)/parseInt(stockAnalysis.numTweets)*100;
            neuTweetsBar.setAttribute('aria-valuenow',neuBarRatio);
            neuTweetsBar.setAttribute('style','width:'+Number(neuBarRatio)+'%; background-color:#c1c1c1;');

            const negTweetsBar = document.getElementById('numNegativeTweets-bar');
            const negBarRatio = parseInt(stockAnalysis.numNegativeTweets)/parseInt(stockAnalysis.numTweets)*100;
            negTweetsBar.setAttribute('aria-valuenow',negBarRatio);
            negTweetsBar.setAttribute('style','width:'+Number(negBarRatio)+'%; background-color:#bf2626;');
        }

        const relevantTweets = document.getElementById('relevant-tweets');
        if (stockAnalysis.topLikedTweetId > 0) {
            relevantTweets.classList.remove('invisible');
            twttr.widgets.createTweet(
                stockAnalysis.topLikedTweetId,
                document.getElementById("featured-tweet-1"),
                {
                    theme: "light"
                }
            );    
        }
        if (stockAnalysis.topRetweetedTweetId > 0) {
            twttr.widgets.createTweet(
                stockAnalysis.topRetweetedTweetId,
                document.getElementById("featured-tweet-2"),
                {
                    theme: "light"
                }
            );    
        }
        if (stockAnalysis.topLikedTweet2Id > 0) {
            twttr.widgets.createTweet(
                stockAnalysis.topLikedTweet2Id,
                document.getElementById("featured-tweet-3"),
                {
                    theme: "light"
                }
            );    
        }

        

    },
    error: function(error) {
        spinnerBox.classList.add('invisible');
        dataBox.classList.remove('invisible');
        console.log('error',error);
        dataBox.innerHTML = '<p>Error. Try reloading the page.</p>';
    }
})