import stanza

#choosing the processors to run on the text
en_nlp = stanza.Pipeline('en',processors='tokenize,mwt,pos,lemma,depparse')

#lists 
list1 = list()
bigrams = list()
numbigrams = list()
pos = list()
neg = list()
negation = ["never","no","nothing","nowhere","noone","none","not","havent","hasnt","hadnt","cant","couldnt","shouldnt","wont","wouldnt","dont","doesnt","didnt","isnt","arent","aint","n't"]
punctuation = ["^","[","]",".",":",";","?","$","!"]

#running the stanza pipeline on input
en_doc = en_nlp("I never owned tesla stock its much to large cap! But i still hate it.")

#initializing global variable sentiment
sentiment = float()

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

for i in range(0,len(list1)):
    if list1[i] not in negation:
        neg.append("nn")
    elif list1[i] in negation:
        neg.append("nstart")

for i in range(0,len(neg)-1):
    if (neg[i]== "nstart") | (neg[i]== "ne") & (list1[i+1] not in punctuation):
        neg[i+1] = "ne"


#creating a list of all bigrams (not all will be used)
for i in range(0,len(list1)-1):
        bigram=list1[i]+" "+list1[i+1]
        bigrams.append(bigram)
        
#running sentiment analysis on bigrams generated
for i in range(0,len(list1)-1):
    searchfile = open("stock_lex.csv", "r")
    for line in searchfile:
        y=line.find("\"",1,len(line))
        x=line.find(bigrams[i])
        if (x == 1) & (y==len(bigrams[i])+1):
            split_line=line.split(",")
            #print(split_line[2])
            if (neg[i] == "nn") | (neg[i] == "nstart"):
                sentiment = sentiment + float(split_line[2])
            elif neg[i] == "ne":
                sentiment = sentiment + float(split_line[3])
            #print(split_line)
            #print(i)
            numbigrams.append(i)
    searchfile.close()

#print(list1)
#print(numbigrams)
#removing bigrams from unigrams
numbigrams.sort(reverse = True)

for g in range(0,(len(numbigrams))):
    if (numbigrams[g] == 0):
        list1.pop(numbigrams[g])
        list1.pop(numbigrams[g])
    elif (numbigrams[g] == (numbigrams[g+1])+1):
        list1.pop(numbigrams[g])
    else:
        #print(numbigrams[g])
        list1.pop(numbigrams[g])
        list1.pop(numbigrams[g])
        neg.pop(numbigrams[g])
        neg.pop(numbigrams[g])

#running sentiment on unigrams
for i in range(0,len(list1)):
    searchfile = open("stock_lex.csv", "r")
    for line in searchfile:
        y=line.find("\"",1,len(line))
        x=line.find(list1[i])
        split_line=line.split(",")
        z=split_line[1]
        if (x == 1) & (y==len(list1[i])+1) & (z==pos[i]):
            if (neg[i] == "nn") | (neg[i] == "nstart"):
                sentiment = sentiment + float(split_line[2])
            elif neg[i] == "ne":
                sentiment = sentiment + float(split_line[3])
    searchfile.close()


#print(list1)
print(sentiment)
#print(pos)
#print(neg)

