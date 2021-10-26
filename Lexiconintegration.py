import stanza

#choosing the processors to run on the text
en_nlp = stanza.Pipeline('en',processors='tokenize,mwt,pos,lemma,depparse')

#lists 
list1 = list()
bigrams = list()
numbigrams = list()

#running the stanza pipeline on input
en_doc = en_nlp("I found it to be boooring ! wrap video")

#initializing global variable sentiment
sentiment = float()

#create a list of all words
print(type(en_doc))
for sentence in en_doc.sentences:
    for word in sentence.words:
        list1.append(word.text)

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
        if (x == 1) & (y==len(list1[i])+1):
            split_line=line.split(",")
            print(split_line[2])
            sentiment = sentiment + float(split_line[2])
            print(split_line)
            print(i)
    searchfile.close()

print(list1)
print(sentiment)
print(numbigrams)


print(bigrams)

