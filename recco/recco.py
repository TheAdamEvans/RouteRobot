from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from statsmodels.distributions.empirical_distribution import ECDF

import pandas as pd
import numpy as np
import re

import itertools


DATA_DIR = '../utah_data/'


def score01(grade, ideal):
    return 1 - abs(ideal - grade)

def scoreb(grade, ideal):
    return grade * ideal

def scale01(feature):
    # always use on an entire column
    ecdf = ECDF(feature.dropna())
    qtile = ecdf(feature)
    scaled_feature = pd.Series(qtile, index=feature.index)
    
    # ECDF says NaN is 1.0
    scaled_feature[pd.isnull(feature)] = float('NaN')
    
    return scaled_feature

def castscale(feature_name, climb, href, diff = True):
    """ Give scores for features with a large range of values """
    casted = climb[feature_name].astype(float)
    scaled = scale01(casted)
    ideal = scaled.loc[href]
    
    if diff:
        scored = map(score01, scaled, itertools.repeat(ideal, len(casted)))
        recco = pd.Series(scored, index=climb.index)
    else:
        recco = pd.Series(scaled, index=climb.index)
    return recco

def match_type(climb, href, type_of_route):
    """ Give scores for climbs that match bouldering, sport, trad, etc."""
    
    collect = []
    for k, v in type_of_route.items():

        # turn boolean into value of 1
        scaled = pd.notnull(climb[k]).astype(int)
        ideal = climb.loc[href][k]

        # score destinations relative to ideal
        scored = map(scoreb, scaled, itertools.repeat(ideal, len(scaled)))
        weighted = pd.Series(np.multiply(scored, v), index=climb.index)

        collect.append(weighted)

    # combine dimensions into one score
    all_type_score = pd.concat(collect, axis = 1)
    type_score = all_type_score.sum(axis='columns')
    return type_score / max(type_score)

def give_recommendation(climb, href, top=10):

    if not href in climb.index:
        print 'href not in climb'
        return

    # isolate description we care about
    combined = climb['description'].astype(str) + climb['other_text'].astype(str)
    descriptive = combined.tolist()

    # lemmatize, tokenize, vectorize text
    tfidf = TfidfVectorizer(
        decode_error='ignore', stop_words='english',
        # max_df = 0.5,
        sublinear_tf=True, ngram_range=(1, 2))
    TFIDF = tfidf.fit_transform(descriptive)

    # reduce dimensionality
    svd = TruncatedSVD(
        n_components=100, random_state=42)
    shrunk = svd.fit_transform(TFIDF)


    ### SCORING ###
    # calculate similarity
    pos = climb.index == href
    sim = cosine_similarity(shrunk[pos], shrunk)
    sim_score = pd.Series(sim[0], index=climb.index)

    # score various columns
    height_score = castscale('feet', climb, href)
    grade_score = castscale('gradeComb', climb, href)
    star_score = castscale('staraverage', climb, href, False)
    vote_score = castscale('starvotes', climb, href, False)

    # these columns are True or NaN
    type_of_route = { 'aid': 1, 'alpine': 1, 'boulder': 1, 'sport': 1, 'trad': 1 , 'ice': 1 }
    type_score = match_type(climb, href, type_of_route)

    # aggregate scores
    charlie = pd.DataFrame({
            'height': height_score,
            'grade': grade_score,
            'stars': star_score,
            'votes': vote_score,
            'sim': sim_score,
            'type': type_score
        })

    # multiply weights
    charlie['sim'] = charlie['sim'] * 25
    charlie['grade'] = charlie['grade'] * 15
    charlie['height'] = charlie['height'] * 5
    charlie['stars'] = charlie['stars'] * 15
    charlie['votes'] = charlie['votes'] * 5
    charlie['type'] = charlie['type'] * 10


    charlie['best'] = charlie.sum(axis='columns')
    charlie.sort_values('best', ascending=False, inplace=True)

    return charlie.index[:top]



climb = pd.read_csv(DATA_DIR + '_climb', index_col = 0)
print "Shape of climb dataframe is", climb.shape

href = '/v/beckeys-wall/105740507'

recco_href = give_recommendation(climb, href)

print climb.loc[recco_href][['rateYDS','rateHueco','starvotes','staraverage','feet','description']]


