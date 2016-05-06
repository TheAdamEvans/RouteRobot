import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer


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
    N = float(X.shape[0])
    # count nonzeros by column
    nnz = np.array((X != 0).sum(0))
    # avoids div by zero error
    nnz[nnz == 0] = 1
    # weight by inverse document frequency
    idf = np.log(N / nnz)

    idf_lookup = dict(zip(vocab, idf[0].tolist()))

    return idf_lookup


def get_sparse_X(text_segments, vocab):
    """ vocab words from description
    returns scipy matrix
    """
    # lemmatize, tokenize, vectorize text
    tfidf = TfidfVectorizer(
        vocabulary=vocab,
        strip_accents = 'unicode', lowercase=True, ngram_range=(1,2),
        norm='l2', sublinear_tf=False, smooth_idf=True, use_idf=True
        )
    X = tfidf.fit_transform(text_segments)
    
    return X


def process_tokens(climb, vocab):
    """ tokenize and count vocab words in sparse matrix of description text """

    X = get_sparse_X(climb['description'], vocab)

    climb['sparse_tfidf'] = [X[i] for i in range(X.shape[0])]
    climb['tokens'] = map(lambda row: get_tokens(row, vocab), X)
    climb['keyword'] = map(lambda t: get_keyword(t), climb['tokens'])

    idf_lookup = calculate_idf_weights(X, vocab)

    return climb, idf_lookup
