from typing import TYPE_CHECKING
import stanza
import time
import csv

stanza.download('en')
#en_nlp = stanza.Pipeline('en',processors='tokenize,mwt,pos,lemma,depparse')
en_nlp = stanza.Pipeline('en',processors='tokenize,pos')


# This file is static and we don't want to read it for each tweet.
# So we just read it once on start up and use it.
stock_lex = open('stock_lex.csv', 'r')
reader = csv.reader(stock_lex)
bigramsDict = {}
unigramDict = {}
for row in reader:
    if(row[1] == ''): # Bigrams are represented by a POS of an empty string
        bigramsDict[row[0]] = {
            "aff_score": row[2],
            "neg_score": row[3]
        }
    else: # if it has a POS value then it is a unigram
        unigramDict[row[0]] = {
            "pos": row[1],
            "aff_score": row[2],
            "neg_score": row[3]
        }
stock_lex.close()

def textSentiment(arg1):
    start = time.time();
    #choosing the processors to run on the text

    #lists 
    list1 = list()
    bigrams = list()
    numbigrams = list()
    pos = list()
    neg = list()
    negation = ["never","no","nothing","nowhere","noone","none","not","havent","hasnt","hadnt","cant","couldnt","shouldnt","wont","wouldnt","dont","doesnt","didnt","isnt","arent","aint","n't"]
    punctuation = ["^","[","]",".",":",";","?","$","!"]


    nlp_start = time.time()
    #running the stanza pipeline on input
    en_doc = en_nlp(arg1)
    nlp_end = time.time()

    #initializing global variable sentiment
    sentiment = float()

    posstart = time.time()

    #create a list of all words and POS
    #print((en_doc))
    for sentence in en_doc.sentences:
        for word in sentence.words:
            list1.append(word.text)
            if (word.pos == "PRON"):
                pos.append("PR")
            elif (word.pos == "ADJ"):
                pos.append("JJ")
            elif (word.pos == "ADP"):
                pos.append("IN")
            elif (word.pos == "ADV"):
                pos.append("RB")
            elif (word.pos == "AUX"):
                pos.append("MD")
            elif (word.pos == "CCONJ"):
                pos.append("CC")
            elif (word.pos == "DET"):
                pos.append("DT")
            elif (word.pos == "INTJ"):
                pos.append("UH")
            elif (word.pos == "NOUN"):
                pos.append("NN")
            elif (word.pos == "NUM"):
                pos.append("CD")
            elif (word.pos == "Part"):
                pos.append("RP")
            elif (word.pos == "PROPN"):
                pos.append("NN")
            elif (word.pos == "SCONJ"):
                pos.append("IN")
            elif (word.pos == "SYM"):
                pos.append("SY")
            elif (word.pos == "VERB"):
                pos.append("VB")
            elif (word.pos == "PUNCT"):
                pos.append("")
            elif (word.pos == "X"):
                pos.append("")
            else: pos.append("")

    for i in range(0,len(list1)):
        if list1[i] not in negation:
            neg.append("nn")
        elif list1[i] in negation:
            neg.append("nstart")

    for i in range(0,len(neg)-1):
        if (neg[i]== "nstart") | (neg[i]== "ne") & (list1[i+1] not in punctuation):
            neg[i+1] = "ne"

    posend = time.time()

    bigramStart = time.time()

    for i in range(0,len(list1)-1):
        bigram = list1[i]+" "+list1[i+1]
        if(bigram in bigramsDict.keys()):
            if (neg[i] == "nn") | (neg[i] == "nstart"):
                sentiment = sentiment + float(bigramsDict[bigram]["aff_score"])
                break
            elif neg[i] == "ne":
                sentiment = sentiment + float(bigramsDict[bigram]["neg_score"])
                break
            #print(split_line)
            #print(i)
            numbigrams.append(i)
        

    bigramEnd = time.time()

    #print(list1)
    #print(numbigrams)
    #removing bigrams from unigrams
    numbigrams.sort(reverse = True)
    

    for g in range(0,(len(numbigrams))):
        if (numbigrams[g] == 0):
            list1.pop(numbigrams[g])
            list1.pop(numbigrams[g])
        elif ((len(numbigrams) > 1) & (g<len(numbigrams)-1)):
            if (numbigrams[g] == (numbigrams[g+1])+1):
                list1.pop(numbigrams[g])
        else:
            #print(numbigrams[g])
            list1.pop(numbigrams[g])
            list1.pop(numbigrams[g])
            neg.pop(numbigrams[g])
            neg.pop(numbigrams[g])

    # unigram
    unigramstart = time.time()
    for i in range(0,len(list1)-1):
        tweet_word = list1[i]
        if tweet_word in unigramDict.keys() and pos[i] == unigramDict[tweet_word]["pos"]:
            if neg[i] == "nn" or neg[i] == "nstart":
                sentiment += float(unigramDict[tweet_word]["aff_score"])
                break
            elif neg[i] == "ne":
                sentiment += float(unigramDict[tweet_word]["neg_score"])
                break

    unigramend = time.time()

    total = time.time() - start
    nlp_total = nlp_end - nlp_start
    pos_total = posend - posstart
    bigram_total = bigramEnd - bigramStart
    unigram_total = unigramend - unigramstart

    totals = {
        "npl": nlp_total, 
        "pos": pos_total, 
        "bigram": bigram_total, 
        "unigram": unigram_total
    }

    #print(f"textSentiment: {str(total)} - {total/total*100}%")
    #for key, value in totals.items():
    #    print(f"    {key}: {str(value)} - {value * 100.0 / total}%")


    # sentiment is typically between -2 and 2 but can go as high as or higher than -5/+5
    # Thus the sentiment is now hard capped between -2 to 2, and converted to be between -1/1
    if sentiment > 2:
        sentiment = 2
    elif sentiment < -2:
        sentiment = -2

    return (sentiment/2)




