# to run summarizer
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
from scipy.spatial import distance
from sklearn.decomposition import PCA
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
import matplotlib.pyplot as plt
import json
import warnings
warnings.filterwarnings("ignore")

#to get input from server
import sys
text = sys.argv[1]
to_server = {}


#preprocessing
# preprocessing step
sentences = nltk.sent_tokenize(text)
lemmatizer = WordNetLemmatizer()
words_by_words = []
wordlist = []
sent_for_keywords = []
for i in range(len(sentences)):
    sentences[i] = contractions.fix(sentences[i])
    sentences[i] = re.sub('[^a-zA-Z]', " ", sentences[i])
    words = []
    words_for_grams = []
    for word in nltk.word_tokenize(sentences[i]):
        word = word.lower()
        if word not in stopwords.words('english') and len(word) > 1:
            words_for_grams.append(word)
            words.append(lemmatizer.lemmatize(word))
            wordlist.append(word)
    sent_for_keywords.append(" ".join(words_for_grams))
    sentences[i] = " ".join(words)
    words_by_words.append(words)
sentence_tokens = sentences

#generating TF-IDF scores
vectorizer = TfidfVectorizer(use_idf=True, ngram_range = (1,3))
vectors = vectorizer.fit_transform(sentence_tokens)
feature_names = vectorizer.get_feature_names()
scores = vectors.todense().tolist()
#word_weights =dict(zip(vectorizer.get_feature_names(), vectorizer.idf_))
tfidf = pd.DataFrame(scores, columns=feature_names)

#generating keywords
from sklearn.feature_extraction.text import CountVectorizer
counter = CountVectorizer(ngram_range = (1,3))
counts = counter.fit_transform(sent_for_keywords)
kwords = counter.get_feature_names()
count_scores = counts.todense().tolist()
tfs = pd.DataFrame(count_scores, columns=kwords)

to_server['keywords'] = tfs.sum(axis=0).nlargest(10).keys().tolist()

#creating wordcloud from text
wordcloud = WordCloud(stopwords=stopwords.words('english'), colormap="Dark2", width=400, height=300,
        max_font_size=50, max_words=100, background_color="white").generate(text)
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

#Visualize Cluster Assignments
three_dim = PCA(random_state=0).fit_transform(sent_vector)[:,:3]
x = []
y = []
z = []
try:
    for i in range(len(three_dim)):
        x.append(three_dim[i,0]*1000)
        y.append(three_dim[i,1]*1000)
        z.append(three_dim[i,2]*1000)
    
    from mpl_toolkits import mplot3d
    #%matplotlib notebook
    fig = plt.figure()
    axes = plt.axes(projection='3d')
    axes.scatter(x,y,z, c=clusters, cmap='Accent', linewidth=1)

except IndexError:
    pass

plt.savefig('public/cluster_viz.png', pad_inches=0, dpi=300)

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

to_server['summary'] = summary

print(json.dumps(to_server))
sys.stdout.flush()
sys.exit()