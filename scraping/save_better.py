import os
import pickle
import pandas as pd

import grade_cleaner as cl
from destination import Destination

from statsmodels.distributions.empirical_distribution import ECDF
from sklearn.feature_extraction.text import TfidfVectorizer


def parse_lat_long(coord):
    if pd.isnull(coord):
        return float('NaN'), float('NaN')
    else:
        return tuple(coord.split(', '))


def scale01(feature):
    """ Scales entire column onto [0,1] using ECDF """

    # fit empirical density
    ecdf = ECDF(feature.dropna())
    # scale values
    qtile = ecdf(feature)
    scaled_feature = pd.Series(qtile, index=feature.index)
    
    # convert NaN from 1.0 back to NaN
    scaled_feature[pd.isnull(feature)] = float('NaN')
    
    return scaled_feature


def grab_children(dest, collect):
    """ Traverses Destination object and return dictionary of features """
    if hasattr(dest, 'children'):
        for child in dest.children:
            collect.append(child.__dict__)
            grab_children(child, collect)
    return collect


def climb_from_dest(dest):
    """ Captures information from Destination object """

    kidnapped = grab_children(dest, collect = []) # kidnapping jokes are not okay
    climb = pd.DataFrame.from_dict(kidnapped) # neither are dict jokes
    if max(climb.shape) > 0:
        climb.set_index(climb.href.values, inplace = True, verify_integrity = True)
        return climb


def combine_pickle(DATA_DIR):
    """ Combines directory of pickled Destination objects into a single DataFrame """
    
    collect_climb = []
    for area in os.listdir(DATA_DIR):
        pkl = '.pickle'
        if area[-len(pkl):] != pkl:
            pass
        else:
            dest = pickle.load(open(DATA_DIR + area, 'rb'))        
            partial = climb_from_dest(dest)
            if partial is not None:
                print 'Found %d destinations in %s' % (partial.shape[0], dest.nickname)
            collect_climb.append(partial)
    climb = pd.concat(collect_climb, axis=0)

    # get rid of embedded Destination objects
    del climb['children']

    return climb


def get_keyword(text_feature, MAX_KEYWORD=20):
    """ Creates a single keyword string for each climb """

    # lemmatize, tokenize, vectorize text
    tfidf = TfidfVectorizer(
        min_df=0.01, max_df=0.1, stop_words = 'english',
        strip_accents = 'unicode', lowercase=True, ngram_range=(1,2),
        norm='l2', smooth_idf=True, sublinear_tf=True, use_idf=True
        )
    text_segments = text_feature.tolist()
    tfidf_matrix = tfidf.fit_transform(text_segments)
    feature_names = tfidf.get_feature_names()

    dense = tfidf_matrix.todense()
    
    description_keyword = []
    for i in range(dense.shape[0]):
        desc = dense[i].tolist()[0]
        phrase_scores = [pair for pair in zip(range(0, len(desc)), desc) if pair[1] > 0]
        sorted_phrase_scores = sorted(phrase_scores, key=lambda t: t[1] * -1)
        
        # pick out and join keywords into a single string
        k = 0
        keyword = []
        for phrase, score in [(feature_names[word_id], score) for (word_id, score) in sorted_phrase_scores]:
            k += 1
            keyword.append(phrase)
            if k == MAX_KEYWORD:
                break
        keyword_summary = "  ".join(keyword)
        description_keyword.append(keyword_summary)
    
    keyword = pd.Series(description_keyword, index=text_feature.index)
    return keyword


def cast_all_pickles(DATA_DIR):
    """ Read in directory of pickles and return workable DataFrame """

    # read in data from directory of pickles
    climb = combine_pickle(DATA_DIR)

    climb['keyword'] = get_keyword(climb['description'])

    # TODO: plit these out into other functions
    # split GPS coordinates into lat long columns
    prsd = map(parse_lat_long, climb['gps_coord'].values)
    lat_long = pd.DataFrame.from_records(prsd, columns = [['latitude','longitude']], index = climb.index)
    climb = pd.concat([climb,lat_long], axis=1)
    climb = climb.drop('gps_coord', axis=1)

    # get rid of lists inside cells
    climb['tree_depth'] = map(len, climb['area_hierarchy'])
    climb['state'] = map(lambda a: a[0], climb['area_hierarchy'])
    climb['area'] = map(lambda a: a[-1], climb['area_hierarchy'])

    climb['num_children'] = map(lambda c: len(c) if isinstance(c,list) else 0, climb['children_href'])
    climb = climb.drop(['area_hierarchy','children_href'], axis=1)
    
    # cast columns appropriately
    numeric_col = ['page_views','elevation','pitches','feet','staraverage','starbest','starvotes','latitude','longitude']
    for col in numeric_col:
        if col in climb.columns:
            climb[col] = pd.to_numeric(climb[col], errors='coerce')

    boolean_col = ['aid','alpine','boulder','sport','trad','ice','mixed','tr','chipped']
    for col in boolean_col:
        if col in climb.columns:
            climb[col] = pd.notnull(climb[col])

    # combine YDS and Hueco grades
    # allows empirical comparison of Bouldering and Sport/Trad routes
    climb['rateFloatHueco'] = map(cl.convert_hueco, climb['rateHueco'])
    climb['ratePCTHueco'] = scale01(climb['rateFloatHueco'])
    #climb['rateFloatYDS'] = map(cl.convert_hueco, climb['rateYDS'])
    #climb['ratePCTYDS'] = scale01(climb['rateFloatYDS'])
    
    # not many conflicting cases -- max is reasonable assuption
    #climb['grade'] = climb[['ratePCTHueco','ratePCTYDS']].max(axis='columns')
    climb['grade'] = climb[['ratePCTHueco']].max(axis='columns')

    return climb