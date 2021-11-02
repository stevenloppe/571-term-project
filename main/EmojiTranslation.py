import csv

def EmojiTranslation(inputList):
    #inputList = ["Eyes", "Rocket", "Gem stone", "Raising hands"]
    sentiments = []
    output = 0.5

    with open("Emoji_Sentiment_Data_v1.0.csv", 'r', encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            name = row[7]
            for item in inputList:
                if (name == item.upper()):
                    negative = int(row[4])
                    neutral = int(row[5])
                    positive = int(row[6])
                    # Formula: ( Positive + Neutral/2 ) / Total
                    sentiment = (positive+neutral/2)/(negative+neutral+positive)
                    sentiments.append(sentiment)

    if (len(sentiments) > 0):
        output = sum(sentiments) / len(sentiments)

    return output
