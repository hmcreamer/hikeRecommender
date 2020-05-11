import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
from lemmatize_trail_descriptions import stop_words

def top_words(clusters, feature_names, num_words):
    idxs = [np.argsort(cluster)[-num_words:][::-1] for cluster in clusters]
    return [feature_names[idx] for idx in idxs]

def topic_word_freq(topics, idx, feature_names):
    '''
    INPUT: topics - Array of word values from nmf_components_
           idx - Topic label to return frequencies for
           feature_names - Array of words from tfidf matrix
    OUTPUT: Array of (word, freq) tuples
    '''
    freq_sum = np.sum(topics[idx])
    frequencies = [val / freq_sum for val in topics[idx]]
    return zip(feature_names, frequencies)

def create_description_vector(df, max_features=5000, max_df=1, min_df=1):
    '''
    INPUTS: df - df['lemmatized_text'] will be what is vectorized
            max_features - number of words to be kept in the TfidfVector
            max_df - Cut off for words appearing in a given threshold of documents. (i.e. 1 = no limit, 0.95 will exclude words appearing in at least 95% of documents from being included in the resulting vector)
            min_df - Cut off for words appearing in a minimum number of documents. (i.e. 2 = term must appear in at least two documents)
    OUTPUT: TfidfVector (X)
            Feature Names Array
            Reverse_lookup Dictionary - Used to quickly and efficiently return the index of a given word in the Feature Names Array
    '''
    stopwords = stop_words()
    tfidf = TfidfVectorizer(input='content', stop_words=stopwords, use_idf=True, lowercase=True, max_features=max_features, max_df=max_df, min_df=min_df)
    X = tfidf.fit_transform(df['lemmatized_text'].values)
    feature_names = np.array(tfidf.get_feature_names())
    reverse_lookup = {word: idx for idx, word in enumerate(feature_names)}
    return X, feature_names, reverse_lookup

def cluster_hikes(df, n_clusters=5, max_features=5000, max_df=1, min_df=1,  num_words=5):
    X, feature_names, reverse_lookup = create_description_vector(df, max_features=max_features, max_df=max_df, min_df=min_df)
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)
    clusters = kmeans.cluster_centers_
    labels = kmeans.labels_
    words = top_words(clusters, feature_names, num_words=num_words)
    return X, kmeans, labels, words


def nmf_descriptions(df, n_topics, n_features=5000, n_top_words=20, random_state=None, max_df=1, min_df=1):
    tfidf, feature_names, reverse_lookup = create_description_vector(df, max_features=n_features, max_df=max_df, min_df=min_df)
    nmf = NMF(n_components=n_topics, random_state=random_state, alpha=.1, l1_ratio=0.25).fit(tfidf)
    W = nmf.transform(tfidf)

    # Currently the attribution for each row in W is not a percentage, but we want to assign each document to any topic which it can be at least 10% attributed to
    sums = np.sum(W, axis=1)
    W_percent = W / sums[:, None]

    # For efficient slicing we will return a sparse boolean array
    labels = W_percent >= 0.1

    words = top_words(nmf.components_, feature_names, n_top_words)
    return nmf, tfidf, W, W_percent, labels, words, feature_names, reverse_lookup

if __name__=='__main__':
    df = pd.read_csv('data/lemmatized_hikes.csv')
    docs = df['lemmatized_text']

    # nmf, tfidf, W, W_percent, labels, topic_words, feature_names, reverse_lookup = nmf_descriptions(df, n_topics=7, n_features=500, random_state=1, max_df=0.8, min_df=0.2)

    X, kmeans, labels, words = cluster_hikes(df, n_clusters=5, max_features=5000, max_df=.3, min_df=0,  num_words=10)

    # cosine_similarities = linear_kernel(tfidf, tfidf)

    # for i, doc1 in enumerate(docs):
    #     for j, doc2 in enumerate(docs):
    #         if cosine_similarities[i, j] < .9 and cosine_similarities[i, j] > .7:
    #             print i, j, cosine_similarities[i, j]
