import stanza

#choosing the processors to run on the text
en_nlp = stanza.Pipeline('en',processors='tokenize,mwt,pos,lemma,depparse')

#lists 
list1 = list()
bigrams = list()
numbigrams = list()
pos = list()

#running the stanza pipeline on input
en_doc = en_nlp("I love that tsla stock it is just good!")

#initializing global variable sentiment
sentiment = float()

#create a list of all words and POS 
print((en_doc))
for sentence in en_doc.sentences:
    for word in sentence.words:
        list1.append(word.text)
        if (word.pos == "PRON"):
            pos.append("PR")
        if (word.pos == "ADJ"):
            pos.append("JJ")
        if (word.pos == "ADP"):
            pos.append("IN")
        if (word.pos == "ADV"):
            pos.append("RB")
        if (word.pos == "AUX"):
            pos.append("MD")
        if (word.pos == "CCONJ"):
            pos.append("CC")
        if (word.pos == "DET"):
            pos.append("DT")
        if (word.pos == "INTJ"):
            pos.append("UH")
        if (word.pos == "NOUN"):
            pos.append("NN")
        if (word.pos == "NUM"):
            pos.append("CD")
        if (word.pos == "Part"):
            pos.append("RP")
        if (word.pos == "PROPN"):
            pos.append("NN")
        if (word.pos == "SCONJ"):
            pos.append("IN")
        if (word.pos == "SYM"):
            pos.append("SY")
        if (word.pos == "VERB"):
            pos.append("VB")
        if (word.pos == "PUNCT"):
            pos.append("")
        if (word.pos == "X"):
            pos.append("")

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
            sentiment = sentiment + float(split_line[2])
            #print(split_line)
            #print(i)
            numbigrams.append(i)
    searchfile.close()

#removing bigrams from unigrams
numbigrams.sort(reverse = True)
for g in range(0,(len(numbigrams))):
    print(numbigrams[g])
    list1.pop(numbigrams[g])
    list1.pop(numbigrams[g])

#running sentiment on unigrams
for i in range(0,len(list1)):
    searchfile = open("stock_lex.csv", "r")
    for line in searchfile:
        y=line.find("\"",1,len(line))
        x=line.find(list1[i])
        split_line=line.split(",")
        z=split_line[1]
        if (x == 1) & (y==len(list1[i])+1) & (z==pos[i]):
            sentiment = sentiment + float(split_line[2])
    searchfile.close()

print(list1)
print(sentiment)
print(pos)


