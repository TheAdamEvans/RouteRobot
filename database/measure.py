import itertools
import numpy as np
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

def scale01(feature):
    """ Uses empirical cumulative density to scale real values to [0,1]
    Always use on an entire column! """
    
    ecdf = ECDF(feature.dropna())

    # fit these observations
    qtile = ecdf(feature)
    scaled_feature = pd.Series(qtile, index=feature.index)
    
    # ECDF says NaN is 1.0
    # this produces a warning
    scaled_feature[pd.isnull(feature)] = float('NaN')
    
    return scaled_feature


def create_scorer(col, feature):
    """
    Creates 3 objects
        - casted (df)
        - scaled (df)
        - scorer (function)
    Different columns take different treatments and methods for scoring
    Goal is to unify feature treatment here
    """
    
    if col in ['aid','alpine','boulder','sport','trad','ice']:

        # turn boolean into value of 1
        casted = pd.notnull(feature)
        scaled = casted.astype(int)
        
        def scorer(grade, ideal):
            return ideal * grade
        
        return casted, scaled, scorer
    
    elif col in ['feet', 'pitches', 'grade']:
        
        casted = feature.astype(float)
        scaled = scale01(casted)
        
        def scorer(grade, ideal):
            return 1 - abs(ideal - grade)
        
        return casted, scaled, scorer
    
    elif col in ['staraverage', 'starvotes']:
        
        casted = feature.astype(float)
        scaled = scale01(casted)
        
        def scorer(grade, ideal):
            return grade
        
        return casted, scaled, scorer
    
    elif col in ['description']:
        
        # lemmatize, tokenize, vectorize text
        tfidf = TfidfVectorizer(
            min_df = 0.01, max_df=0.2, stop_words = 'english',
            strip_accents = 'unicode', lowercase=True, ngram_range=(1,2),
            norm='l2', sublinear_tf=True
            )
        text_segments = feature.tolist()
        casted = tfidf.fit_transform(text_segments)

        # reduce dimensionality
        svd = TruncatedSVD(
            n_components=100, random_state=42)
        scaled = svd.fit_transform(casted)
        scaled = pd.DataFrame(scaled, index=feature.index)

        def scorer(scaled, ideal):
            # sklearn wants you to .reshape
            sim = cosine_similarity(ideal.reshape(1,-1), scaled)
            sim_score = pd.Series(sim[0], index=feature.index)
            return sim_score.tolist()
        
        return casted, scaled, scorer
    
    else:
        return None, None, None


def create_recommendation_system(climb):
    """ Appropriately fit models to all climbs """

    # iterate over columns and fit various representations
    FIT = {}
    for col, feature in climb.iteritems():
        casted, scaled, scorer = create_scorer(col, feature)
        if casted is not None:
            scoring_package = { col: [casted, scaled, scorer] }
            FIT.update(scoring_package)
            
    return FIT


def give_recommendation(FIT, href, top):
    """ Given fit of the various columns as a dict, score this href """

    score_collect = []
    for col, fit in FIT.items():
        casted, scaled, scorer = fit
        ideal = scaled.loc[href]
        if len(scaled.shape) == 1:
            # most features are scored like this
            score = map(scorer, scaled, itertools.repeat(ideal, len(scaled)))
        else:
            # only for description text scoring
            score = scorer(scaled, ideal)
        
        score = pd.DataFrame({ col: score }, index=scaled.index)
        score_collect.append(score)
    # concatenate scores into a DataFrame
    rec = pd.concat(score_collect, axis=1)
    
    # multiply weights
    # magic numbers because obviously
    rec['description'] = rec['description'] * 35
    rec['grade'] = rec['grade'] * 12
    rec['feet'] = rec['feet'] * 10
    rec['pitches'] = rec['pitches'] * 3
    rec['staraverage'] = rec['staraverage'] * 15
    rec['starvotes'] = rec['starvotes'] * 5
    rec['boulder'] = rec['boulder'] * 2
    rec['sport'] = rec['sport'] * 2
    rec['trad'] = rec['trad'] * 2
    # rec['ice'] = rec['ice'] * 4
    
    rec['best'] = rec.sum(axis=1)
    rec.sort_values('best', ascending=False, inplace=True)
    # format for web
    rec['best'] = (100 * rec['best'] / max(rec['best'])).round()

    # top recommendation is always self
    return rec[0:top+1]