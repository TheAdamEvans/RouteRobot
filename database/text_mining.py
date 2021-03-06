import numpy as np
import pandas as pd

from scipy.linalg import norm
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD


def get_keyword(tokens, MAX_KEYWORD=20):
    """ pick out and join keywords into a single string """
    if isinstance(tokens, list):
        MAX_KEYWORD = min(len(tokens),MAX_KEYWORD)
        keyword = '  '.join(tokens[:MAX_KEYWORD])
        return keyword
    else:
        return ''


def get_tokens(row, vocab):
    """ translates sparse vector into relevancy-ordered tokens"""
    badsort_tokens = [vocab[loc] for loc in row.nonzero()[1]]
    badsort_values = [row[0,loc] for loc in row.nonzero()[1]]
    sorted_tokens = sorted(zip(badsort_values, badsort_tokens), reverse=True)
    tokens = [t for (v,t) in sorted_tokens]
    return tokens


def calculate_idf_weights(X, vocab):
    """ weight each word by inverse document frequency """
    N = float(X.shape[0])
    # count nonzeros by column
    nnz = np.array((X != 0).sum(0))
    # avoids div by zero error
    nnz[nnz == 0] = 1
    # weight by inverse document frequency
    idf = np.log(N / nnz)

    idf_lookup = dict(zip(vocab, idf[0].tolist()))

    return idf_lookup


def vectorize_vocab(text_segments, vocab):
    """ vocab words from description
    returns scipy matrix, low rank numpy matrix, svd components
    """
    # lemmatize, tokenize, vectorize text
    tfidf = TfidfVectorizer(
        vocabulary=vocab,
        strip_accents = 'unicode', lowercase=True, ngram_range=(1,2),
        norm='l2', sublinear_tf=False, smooth_idf=True, use_idf=True
        )
    X = tfidf.fit_transform(text_segments)
    
    # project sparse vocab space into lower rank dense represenation
    svd = TruncatedSVD(
        n_components=256, random_state=42
        )
    low_rank_X = svd.fit_transform(X)

    return X, low_rank_X, svd.components_


# def combine_sparse_matrix(cmb, route_description_weight = 1.618):
#     """ Add sparse representations of route and area descriptions together """
# 
#     if pd.isnull(cmb['parent_sparse_tfidf']):
#         if pd.isnull(cmb['sparse_tfidf']):
#             return float('NaN')
#         else:
#             return cmb['sparse_tfidf']
#     else:
#         area = np.array(cmb['parent_sparse_tfidf'].todense())
#         route = np.array(cmb['sparse_tfidf'].todense()) * route_description_weight
#         added = area + route
#         # L2 normalize again
#         text_vector = added / norm(added, 2)
#         return csr_matrix(text_vector)


def combine_dense_matrix(climb, route_description_weight = 1.618):
    """ Add dense representations of route and area descriptions together """
    collect = []
    for _, cmb in climb.iterrows():
        if isinstance(cmb['parent_dense_tfidf'],float):
            if isinstance(cmb['dense_tfidf'],float):
                collect.append(float('NaN'))
            else:
                collect.append(cmb['dense_tfidf'])
        else:
            area = cmb['parent_dense_tfidf']
            route = cmb['dense_tfidf'] * route_description_weight
            added = area + route * route_description_weight
            # L2 normalize again
            text_vector = added / norm(added, 2)
            collect.append(text_vector)
    return collect


def process_tokens(climb, vocab):
    """ tokenize and count vocab words in sparse matrix of description text
    return idf weights for each word, projection matrix
    """

    X, low_rank_X, svd_comp = vectorize_vocab(climb['description'], vocab)

    climb['sparse_tfidf'] = [X[i] for i in range(X.shape[0])]
    climb['dense_tfidf'] = [low_rank_X[i] for i in range(len(low_rank_X))]
    climb['tokens'] = map(lambda row: get_tokens(row, vocab), X)
    climb['keyword'] = map(lambda t: get_keyword(t), climb['tokens'])

    idf_lookup = calculate_idf_weights(X, vocab)

    return climb, idf_lookup, svd_comp
