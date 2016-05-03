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


def sanitize(dirty_query, vocab):
    """ Transform query string into vocab tokens """
    query = dirty_query.strip().lower()
    unigrams = query.split(' ')
    bigrams = [ b[0]+' '+b[1] for l in [query] for b in zip(l.split(' ')[:-1], l.split(' ')[1:]) ]
    tokens = [ t for t in (unigrams + bigrams) if t in vocab ]
    return tokens


def get_keyword(tokens, MAX_KEYWORD=20):
    # pick out and join keywords into a single string
    MAX_KEYWORD = min(len(tokens),MAX_KEYWORD)
    keyword = '  '.join(tokens[:MAX_KEYWORD])
    return keyword


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
    # initalize flattening with self to get top level info too!
    kidnapped = grab_children(dest, collect = [dest.__dict__]) # kidnapping jokes are not okay
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


def get_climb_type(cmb, ordered_bool_col):
    """ Break ties for many multlple-types climbs """
    type_of_climb = cmb[ordered_bool_col]
    if sum(type_of_climb) == 0:
        typ = float('NaN')
    else:
        for typ, is_typ in type_of_climb.iteritems():
            if is_typ:
                break
    return typ


def get_parent_datum(climb, col, depth=2):
    """ Lookup information from areas with specified depth
    Parents have depth -2 because self.href is last
    """
    collect = []
    for cmb in climb['href']:
        parent_href = climb.loc[cmb]['hierarchy']
        if len(parent_href) < depth:
            pdatum = float('NaN')
        else:
            pdatum = climb.loc[parent_href][col][-depth]
        collect.append(pdatum)
    return pd.Series(collect, index=climb.index)


def get_coord(hierarchy, climb):
    """ Recursively seeks a non null gps coordinate from the hierarchy """
    coord = climb.loc[hierarchy[-1]]['gps_coord']
    if isinstance(coord, str):
        return coord
    else:
        hierarchy = hierarchy[:-1]
        if len(hierarchy) == 0:
            return float('NaN')
        else:
            coord = get_coord(hierarchy, climb)
            return coord


def cast_all_pickles(DATA_DIR):
    """ Read in directory of pickles and return workable DataFrame """

    # read in data from directory of pickles
    climb = combine_pickle(DATA_DIR)

    # grab vocab words from the description
    print 'Tokenizing...'
    vocab = pd.read_csv('bigram_vocab.txt', header=None)[0].tolist()
    climb['tokens'] = map(lambda c: sanitize(c,vocab), climb['description'])
    climb['keyword'] = map(lambda t: get_keyword(t), climb['tokens'])

    # split GPS coordinates into lat long columns
    prsd = map(parse_lat_long, climb['gps_coord'].values)
    lat_long = pd.DataFrame.from_records(prsd, columns = [['latitude','longitude']], index = climb.index)
    climb = pd.concat([climb,lat_long], axis=1)


    # cast columns appropriately
    num_col = [
        'page_views','elevation','pitches','feet',
        'staraverage','starbest','starvotes','latitude','longitude'
        ]
    for col in num_col:
        if col in climb.columns:
            climb[col] = pd.to_numeric(climb[col], errors='coerce')
    bool_col = [
        'mixed','ice','tr','boulder','aid','trad','sport','alpine','chipped'
        ]
    for col in bool_col:
        if col in climb.columns:
            climb[col] = pd.notnull(climb[col])


    # leverage then delete area_hierarchy
    # quick counts for posterity
    print 'Area hierarchy...'
    climb['tree_depth'] = map(len, climb['hierarchy'])
    climb['num_children'] = map(lambda c: len(c) if isinstance(c,list) else 0, climb['children_href'])

    # for climbs with multiple types pick one
    climb['single_climb_type'] = climb.apply(get_climb_type, axis=1, args=(bool_col,))

    # what state is this climb in
    climb['state_name'] = get_parent_datum(climb, 'name', depth=0)

    # grab info from immediate parents
    climb['parent_tokens'] = get_parent_datum(climb, 'tokens')
    climb['parent_keyword'] = get_parent_datum(climb, 'keyword')
    climb['parent_name'] = get_parent_datum(climb, 'name')
    climb['total_token'] = climb['parent_tokens'] + climb['tokens']
    climb['parent_gps_coord'] = get_parent_datum(climb, 'gps_coord')

    # find best gps coords available
    # climb['gps_coord_inferred'] = map(lambda h: get_coord(h, climb), climb['hierarchy'])

    # get rid of lists inside dataframe
    climb = climb.drop(['hierarchy','children_href'], axis=1)
    

    ## scale columns on [0,1] to make scoring easier later
    climb['scaledFeet'] = scale01(climb['feet'])
    climb['scaledPitches'] = scale01(climb['pitches'])


    # cast grade strings as float
    climb['rateFloatHueco'] = map(cl.convert_hueco, climb['rateHueco'])
    climb['rateFloatYDS'] = map(cl.convert_hueco, climb['rateYDS'])
    climb['ratePCTHueco'] = scale01(climb['rateFloatHueco'])
    climb['ratePCTYDS'] = scale01(climb['rateFloatYDS'])

    # combine YDS and Hueco grades
    # allows empirical comparison of Bouldering and Sport/Trad routes
    # not many conflicting cases -- max is reasonable assuption
    climb['grade'] = climb[['ratePCTHueco','ratePCTYDS']].max(axis='columns')

    return climb