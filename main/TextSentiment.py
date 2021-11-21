import stanza
import time

stanza.download('en')
#en_nlp = stanza.Pipeline('en',processors='tokenize,mwt,pos,lemma,depparse')
en_nlp = stanza.Pipeline('en',processors='tokenize,pos')

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

    #creating a list of all bigrams (not all will be used)
    for i in range(0,len(list1)-1):
            bigram=list1[i]+" "+list1[i+1]
            bigrams.append(bigram)
            
    #running sentiment analysis on bigrams generated
    searchfile = open("stock_lex.csv", "r")
    for i in range(0,len(list1)-1):
        for line in searchfile:
            y=line.find("\"",1,len(line))
            x=line.find(bigrams[i])
            if (x == 1) & (y==len(bigrams[i])+1):
                split_line=line.split(",")
                #print(split_line[2])
                if (neg[i] == "nn") | (neg[i] == "nstart"):
                    sentiment = sentiment + float(split_line[2])
                    break
                elif neg[i] == "ne":
                    sentiment = sentiment + float(split_line[3])
                    break
                #print(split_line)
                #print(i)
                numbigrams.append(i)


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

    bigramEnd = time.time()


    unigramstart = time.time()
    #running sentiment on unigrams
    for i in range(0,len(list1)-1):
        for line in searchfile:
            y=line.find("\"",1,len(line))
            x=line.find(list1[i])
            split_line=line.split(",")
            z=split_line[1]
            if (x == 1) & (y==len(list1[i])+1) & (z==pos[i]):
                if (neg[i] == "nn") | (neg[i] == "nstart"):
                    sentiment = sentiment + float(split_line[2])
                    break
                elif neg[i] == "ne":
                    sentiment = sentiment + float(split_line[3])
                    break
    unigramend = time.time()

    searchfile.close()


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

    print(f"textSentiment: {str(total)} - {total/total*100}%")
    for key, value in totals.items():
        print(f"    {key}: {str(value)} - {value * 100.0 / total}%")

    return sentiment




