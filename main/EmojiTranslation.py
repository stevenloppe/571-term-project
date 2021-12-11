import csv


def emojiSentiment(inputList):

    #inputList = ['🤷\u200d♂️', '✊', '✊🏻', '✊🏿']
    for i in range(len(inputList)):
        inputList[i] = inputList[i][:1]

    sentiments = []
    output = 0.5

    with open("Emoji_Sentiment_Data_v1.0.csv", 'r', encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            name = row[7]
            emoji = row[0]
            for item in inputList:
                if item.find(emoji) != -1:
                    negative = int(row[4])
                    neutral = int(row[5])
                    positive = int(row[6])
                    # Formula: ( Positive + Neutral/2 ) / Total
                    sentiment = (positive+neutral/2)/(negative+neutral+positive)
                    sentiments.append(sentiment)

    if (len(sentiments) > 0):
        output = sum(sentiments) / len(sentiments)

    # Positive sentiment = output
    # Negative sentiment = 1 - output

    return output