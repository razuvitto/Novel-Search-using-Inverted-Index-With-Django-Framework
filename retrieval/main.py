# Coded with <3 Razuvitto
# location : retrieval/main.py
# April 2018

## // IMPORT LIBRARY // ##
from django.core.files.storage import default_storage
import string
import re
from sklearn.feature_extraction.text import CountVectorizer
from IPython.display import display
import pandas as pd
import numpy as np
import time
import xml.dom.minidom as minidom

collection = minidom.parse("retrieval/collections/novel-data.xml")

# Ambil hanya nomer dokumen dan isi dokumen dari file sample.xml
doc_no = collection.getElementsByTagName('DOCNO')
text = collection.getElementsByTagName('Text')
titles = collection.getElementsByTagName('Title')
author = collection.getElementsByTagName('Author')
cover = collection.getElementsByTagName('Cover')

# Simpan length of document number kedalam variabel N_DOC
N_DOC = len(doc_no)

def detail():
    doc_text = []
    for i in range(N_DOC):
        sentence = text[i].firstChild.data
        doc_text.append(sentence)
    
    doc_number = []
    for i in range(N_DOC):
        number = int(doc_no[i].firstChild.data)
        doc_number.append(number)
        
    doc_title = []
    for i in range(N_DOC):
        title = titles[i].firstChild.data
        doc_title.append(title)

    doc_author = []
    for i in range(N_DOC):
        auth = author[i].firstChild.data
        doc_author.append(auth)

    doc_cover = []
    for i in range(N_DOC):
        cvr = cover[i].firstChild.data
        doc_cover.append(cvr)

    pjg = []
    for i in range(1, (len(doc_title) + 1)):
        pjg.append(i)

    dict_title = dict(zip(pjg, doc_title))
    dict_author = dict(zip(pjg, doc_author))
    dict_text = dict(zip(pjg, doc_text))
    dict_cover = dict(zip(pjg, doc_cover))
    
    return dict_title, dict_author, dict_text, dict_cover

doc_text = []
for i in range(N_DOC):
    sentence = text[i].firstChild.data
    doc_text.append(sentence)
    
doc_number = []
for i in range(N_DOC):
    number = doc_no[i].firstChild.data
    doc_number.append(number)
    
doc_title = []
for i in range(N_DOC):
    title = titles[i].firstChild.data
    doc_title.append(title)

doc_author = []
for i in range(N_DOC):
    auth = author[i].firstChild.data
    doc_author.append(auth)

# [ 1. Tokenization ]
def remove_punc_tokenize(sentence): 
    tokens = []
    
    for w in CountVectorizer().build_tokenizer()(sentence):
        tokens.append(w)
    return tokens

tokens_doc = []
for i in range(N_DOC):
    tokens_doc.append(remove_punc_tokenize(doc_text[i]))
    
# [ 2. Case Folding ]
def to_lower(tokens):
    tokens = [x.lower() for x in tokens]
    return tokens

for i in range(N_DOC):
    tokens_doc[i] = to_lower(tokens_doc[i])
    
# [ 3. Stopping ]
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

def stop_word_token(tokens):
    tokens = [w for w in tokens if not w in stop_words]
    return tokens

for i in range(N_DOC):
    tokens_doc[i] = stop_word_token(tokens_doc[i])
    
# [ 4. Normalization (Stemmer) ] 
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()
def stemming(tokens):
    for i in range(0, len(tokens)):
        if (tokens[i] != stemmer.stem(tokens[i])):
            tokens[i] = stemmer.stem(tokens[i])
    return tokens

for i in range(N_DOC):
    tokens_doc[i] = stemming(tokens_doc[i])

# [ 5. Indexing (Proximity Index) ]
from itertools import count
import collections

all_tokens = []
for i in range(N_DOC):
    for w in tokens_doc[i]:
        all_tokens.append(w)

new_sentence = ' '.join([w for w in all_tokens])

all_tokens = set(all_tokens)

try:
    from itertools import izip as zip
except ImportError:
    pass
proximity_index = {}

# Proses Indexing
for token in all_tokens:
    dict_doc_position = {}
    for n in range(N_DOC):
        if(token in tokens_doc[n]):
            dict_doc_position[doc_no[n].firstChild.data] = [i for i, j in zip(count(), tokens_doc[n]) if j == token]
    proximity_index[token] = dict_doc_position
    
proximity_index = collections.OrderedDict(sorted(proximity_index.items()))

# Proximity Index
# Proses penulisan indeks kedalam file txt
file = open("Indexing-Result.txt",'w')

for key, value in proximity_index.items():
    file.write(key+'\n')
    for key, value in value.items():
        file.write('\t'+str(key)+': ')
        for i in range (len(value)):
            file.write(str(value[i]))
            if not(i == len(value)-1):
                file.write(',')
        file.write('\n')
    file.write('\n')
file.close() 

def main(input_text):

    start = time.time()

    # [ 6. Ranked Retrieval ]
    ## > TFIDF (Term Weighting)

    # QUERY
    query = input_text
    list_of_query = [query.split()]
    # print('\n')

    ### Query Preprocessing
    # Stopwords Process
    for i in range(len(list_of_query)):
        list_of_query[i] = [w for w in list_of_query[i] if not w in stopwords.words('english')]
        
    # Case Folding Process
    for i in range(len(list_of_query)):
        list_of_query[i] = [kata.lower() for kata in list_of_query[i]]
        
    # Stemming Process
    for i in range(len(list_of_query)):
        list_of_query[i] = [stemmer.stem(kata) if kata!=stemmer.stem(kata) else kata for kata in list_of_query[i]]
        
    queries = []
    for i in range(len(list_of_query)):
        for kata in list_of_query[i]:
            if not kata in queries:
                queries.append(kata)


                    
    import math
    N = len(tokens_doc)
    df = []
    res = []

    for i in range(len(queries)):
        sums = 0
        for j in range(len(tokens_doc)):
            if queries[i] in tokens_doc[j]:
                sums += 1
        df.append(sums)

    for i in range(len(df)):
        bobot_res = df[i]
        if bobot_res > 0:
            res.append(math.log10(N / df[i]))
        else:
            res.append(100)
        
    # Weight
    weight = []

    for i in range(len(queries)):
        lists = []
        for j in range(len(tokens_doc)):
            dicts = {}
            x = tokens_doc[j].count(queries[i])
            if x == 0:
                dicts[j+1] = 0
                lists.append(dicts)
            else:
                score = math.log10(x)
                score += 1
                score *= res[i]
                dicts[j+1] = score
                lists.append(dicts)
        weight.append(lists)


    result = []
    for i in range(len(list_of_query)):
        l = []
        for j in range(len(tokens_doc)):
            dic = {}
            for kata in list_of_query[i]:
                sums = 0
                ind = queries.index(kata)
                #print(ind)
                for val in weight[ind][j].values():
                    sums += val
            if(sums!= 0):
                dic['docno'] = j+1
                dic['score'] = sums
                dic['title'] = doc_title[j]
                dic['text'] = doc_text[j]
                dic['author'] = doc_author[j]             
            if(len(dic) != 0): l.append(dic)
        result.append(l)

        
    for i in range(len(list_of_query)):
        result[i] = sorted(result[i], key = lambda x : x['score'], reverse = True)

    # > Cosine Similarity Score
    freq = []
    for i in range(len(queries)):
        s = 0
        for x in range(len(list_of_query)):
            if queries[i] in list_of_query[x]:
                s += 1
        freq.append(s)

    resultqueries = []
    for i in range(len(freq)):
        resultqueries.append(math.log10(N / freq[i]))
        

    weightqueries = []
    for i in range(len(queries)):
        lists = []
        for j in range(len(list_of_query)):
            dicts = {}
            x = list_of_query[j].count(queries[i])
            if x == 0:
                dicts[j+1] = 0
                lists.append(dicts)
            else:
                score = math.log10(x)
                score += 1
                score *= resultqueries[i]
                dicts[j+1] = score
                lists.append(dicts)
        weightqueries.append(lists)

        
    import math
    new_weight = []

    for i in range(len(queries)):
        lists = []
        for j in range(len(tokens_doc)):
            dicts = {}
            x = tokens_doc[j].count(queries[i])
            if x == 0:
                dicts[j+1] = 0
                lists.append(dicts)
            else:
                score = math.log10(x)
                score += 1
                dicts[j+1] = score  
                lists.append(dicts)
        new_weight.append(lists)
        
        
    normalize = []
    for i in range(len(queries)):
        ss = []
        g = 0
        for x in weightqueries[i]:
            for val in x.values():
                if val!=0: ss.append(val)
        for c in ss:
            g = g + math.pow(c,2)
        normalize.append(math.sqrt(g))


    for i in range(len(queries)):
        for x in weightqueries[i]:
            for key,val in x.items():
                val = val / normalize[i]
                x[key] = val
                

    length2 = len(tokens_doc)
    normalization = []            
    for i in range(len(queries)):
        ss = []
        g = 0
        for x in new_weight[i]:
            for val in x.values():
                if val != 0: ss.append(val)
        for c in ss:
            g = g + math.pow(c,2)
        normalization.append(math.sqrt(g))
        

    for i in range(len(queries)):
        for x in new_weight[i]:
            for key,val in x.items():
                if normalization[i] > 0:
                    val = val / normalization[i]
                    x[key] = val
                else:
                    val = 100
                    x[key] = val

                
    result_cosine = []
    for i in range(len(list_of_query)):
        hasilcosine  = []
        for j in range(len(tokens_doc)):
            dix  = {}
            ans = []
            for kata in list_of_query[i]:
                ind = queries.index(kata)
                for x,y in zip(weightqueries[ind][i].values(),new_weight[ind][j].values()):
                    ans.append(x*y)
    
            if sum(ans)!=0:
                dix['docno'] = j+1
                dix['score'] = sum(ans)
                dix['title'] = doc_title[j]
                dix['text'] = doc_text[j]
                dix['author'] = doc_author[j] 
            if len(dix) != 0: hasilcosine.append(dix)
        result_cosine.append(hasilcosine)
        
        
    xx = result_cosine
    for i in range(len(list_of_query)):
        result_cosine[i] = sorted(result_cosine[i], key = lambda x : x['score'], reverse = True)

        
    top_res = result_cosine[0]
    
    if val == 100:
        top_result = top_res[:0]
    else:
        top_result = top_res
    
    # print('Result :')
    top_result

    attrs = {}
    for value in top_result:
        attrs[value["docno"]] = value["title"], value["score"], value["text"], value["author"]
        
    idnya = []
    scorenya = []
    judulnya = []
    isinya = []
    authornya = []
    for i,j in attrs.items():
        idnya.append(i)
        judulnya.append(j[0])
        scorenya.append(j[1])
        isinya.append(j[2])
        authornya.append(j[3])

    proximity = proximity_index.items()

    end = time.time()
    execute_time = end - start

    return top_result, query, execute_time, idnya, scorenya, judulnya, isinya, authornya, attrs, proximity, query, queries
