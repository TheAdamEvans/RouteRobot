import os
import pickle
import pandas as pd
import cleaner as cl
from Destination import Destination
from statsmodels.distributions.empirical_distribution import ECDF

DATA_DIR = 'berk_data/'
SAVE_AS = 'climb.csv'


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
            collect_climb.append(partial)
    climb = pd.concat(collect_climb, axis=0)

    # get rid of embedded Destination objects
    del climb['children']

    return climb


if __name__ == '__main__':

    # track of columns in need of casting
    numeric_col = ['page_views','pitches','feet','staraverage','starbest','starvotes']
    boolean_col = ['boulder','chipped','sport','trad','tr']

    # read in data from directory of pickles
    climb = combine_pickle(DATA_DIR)
    print 'Found %d destinations in %s' % (climb.shape[0], DATA_DIR)
    
    # cast columns appropriately
    for col in numeric_col:
        if col in climb.columns:
            climb[col] = pd.to_numeric(climb[col], errors='coerce')
    for col in boolean_col:
        if col in climb.columns:
            climb[col] = pd.notnull(climb[col])

    # combine YDS and Hueco grades
    # allows empirical comparison of Bouldering and Sport/Trad routes
    climb['rateFloatHueco'] = map(cl.convert_hueco, climb['rateHueco'])
    climb['ratePCTHueco'] = scale01(climb['rateFloatHueco'])
    climb['rateFloatYDS'] = map(cl.convert_hueco, climb['rateYDS'])
    climb['ratePCTYDS'] = scale01(climb['rateFloatYDS'])
    
    # not many conflicting cases -- max is reasonable assuption
    climb['grade'] = climb[['ratePCTHueco','ratePCTYDS']].max(axis='columns')
    
    climb.to_csv(DATA_DIR + SAVE_AS)