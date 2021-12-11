import csv


EmojiSentimentTable = []
with open("Emoji_Sentiment_Data_v1.0.csv", 'r', encoding="utf8") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        EmojiSentimentTable.append([row[0],row[4],row[5],row[6],row[7]]) # emoji, negative, neutral, positive, name


def emojiSentiment(inputList):


    #inputList = ['🤷\u200d♂️', '✊', '✊🏻', '✊🏿']
    for i in range(len(inputList)):
        inputList[i] = inputList[i][:1]

    sentiments = []
    output = 0.5

    for row in EmojiSentimentTable:
        name = row[4]
        emoji = row[0]
        for item in inputList:
            if item.find(emoji) != -1:
                negative = int(row[1])
                neutral = int(row[2])
                positive = int(row[3])
                # Formula: ( Positive + Neutral/2 ) / Total
                sentiment = (positive+neutral/2)/(negative+neutral+positive)
                sentiments.append(sentiment)

    if (len(sentiments) > 0):
        output = sum(sentiments) / len(sentiments)

    return output
