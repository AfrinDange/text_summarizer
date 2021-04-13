# to run summarizer
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from scipy.spatial import distance
import pandas as pd
import numpy as np
from gensim.models import Word2Vec
import contractions
import json
import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import warnings
warnings.filterwarnings("ignore")

#to get input from server
import sys
text = sys.argv[1]


#preprocessing
sentences = nltk.sent_tokenize(text)
if int(0.30*len(sentences)) < 1:
    print("Text Too Short to Summarize!")
    sys.exit()
lemmatizer = WordNetLemmatizer()
words_by_words = []
for i in range(len(sentences)):
    sentences[i] = contractions.fix(sentences[i])
    sentences[i] = re.sub('[^a-zA-Z]', " ", sentences[i])
    words = []
    for word in nltk.word_tokenize(sentences[i]):
        if word.lower() not in stopwords.words('english') and len(word) > 1:
            words.append(lemmatizer.lemmatize(word.lower()))
    sentences[i] = " ".join(words)
    words_by_words.append(words)
sentence_tokens = sentences

#generating TF-IDF scores
vectorizer = TfidfVectorizer(use_idf=True)
vectors = vectorizer.fit_transform(sentence_tokens)
feature_names = vectorizer.get_feature_names()
scores = vectors.todense().tolist()
word_weights = dict(zip(vectorizer.get_feature_names(), vectorizer.idf_))
tfidf = pd.DataFrame(scores, columns=feature_names)

#creating wordcloud from text
wordcloud = WordCloud(stopwords=stopwords.words('english'), max_font_size=50, max_words=100, background_color="white").generate(text)
wordcloud.to_file("public/wordcloud.png")


#Generating Word Embeddings
model = Word2Vec(words_by_words, min_count=1, sg=1) # sg=1 -> skip gram and sg=0 -> cbow
sent_vector = []
empty_vecs = []

#Generating Sentence vectors
for i in range(len(sentence_tokens)):
    word_em = 0
    for word in sentences[i].split():
        try:
            word_em += tfidf.iloc[i][word]*model.wv[word]
        except KeyError:
            pass
    if len(sentences[i].split()) == 0:
        word_em = 0
        empty_vecs.append(i)
    else:
        word_em /= len(sentences[i].split())
        sent_vector.append(word_em)


n_clusters = int(0.30*len(sentence_tokens))
kmeans = KMeans(n_clusters, init='k-means++', random_state=42)
clusters = kmeans.fit_predict(sent_vector)

# adjusting empty sentences
clusters = clusters.tolist()
for i in empty_vecs:
    clusters.insert(i, np.nan)
    sent_vector.insert(i, np.nan)
clusters = np.asarray(clusters)

#selecting sentences to add in summary
sent_idx = []
sentences = nltk.sent_tokenize(text)
for i in range(n_clusters):
    dist = {}
    for j in range(len(clusters)):
        if clusters[j] == np.nan:
            continue
        elif clusters[j] == i:
            dist[j] = distance.euclidean(
                kmeans.cluster_centers_[i], sent_vector[j])
            min_distance = min(dist.values())
            sent_idx.append(min(dist, key=dist.get))

sent_idx = sorted(set(sent_idx))
summary = []
for i in sent_idx:
    summary.append(sentences[i])
summary = "".join(summary)

#to_server = {}
#to_server['summary'] = summary

print(summary)
sys.stdout.flush()
sys.exit()