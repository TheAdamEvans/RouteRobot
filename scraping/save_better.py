import os
import pickle
import pandas as pd

from destination import Destination
from grade_cleaner import convert_string_grade

from statsmodels.distributions.empirical_distribution import ECDF


def parse_lat_long(coord):  
    if pd.isnull(coord):
        return float('NaN'), float('NaN')
    else:
        return tuple(coord.split(', '))


def get_climb_type(cmb, ordered_bool_col):
    """ assign a single climb type """
    type_of_climb = cmb[ordered_bool_col]
    if sum(type_of_climb) == 0:
        typ = float('NaN')
    else:
        for typ, is_typ in type_of_climb.iteritems():
            if is_typ:
                break
    return typ


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


def recurse_datum(hierarchy, datum, climb):
    """ Recursively seeks a non null column value from the hierarchy """
    coord = climb.loc[hierarchy[-1]][datum]
    if isinstance(coord,(str,list,int)):
        return coord
    else:
        hierarchy = hierarchy[:-1]
        if len(hierarchy) == 0:
            return float('NaN')
        else:
            coord = recurse_datum(hierarchy, datum, climb)
            return coord


def cast_all_pickles(DATA_DIR):
    """ From directory of pickles return workable DataFrame """

    # read in data from directory of pickles
    climb = combine_pickle(DATA_DIR)
    climb = climb.sort_index()

    # find best gps coords available
    climb['gps_coord_inferred'] = map(lambda a: recurse_datum(a,'gps_coord',climb), climb['hierarchy'])
    # split GPS coordinates into lat long columns
    prsd = map(parse_lat_long, climb['gps_coord_inferred'].values)
    lat_long = pd.DataFrame.from_records(prsd, columns = [['latitude','longitude']], index = climb.index)
    climb = pd.concat([climb,lat_long], axis=1)

    # cast various columns appropriately
    num_col = [
        'page_views','elevation','pitches','feet',
        'staraverage','starbest','starvotes','latitude','longitude'
        ]
    for col in num_col:
        if col in climb.columns:
            climb[col] = pd.to_numeric(climb[col], errors='coerce')
    bool_col = [
        'mixed','ice','aid','tr','alpine','trad','sport','chipped','boulder'
        ]
    for col in bool_col:
        if col in climb.columns:
            climb[col] = pd.notnull(climb[col])

    # Flask doesn't like 'name' as a header
    climb['dest_name'] = climb['name']

    # pick one type descriptor
    climb['single_climb_type'] = climb.apply(get_climb_type, axis=1, args=(bool_col,))

    # scale columns on [0,1] to make scoring easier later
    climb['scaledFeet'] = scale01(climb['feet'])
    climb['scaledPitches'] = scale01(climb['pitches'])
    climb['scaledStarvotes'] = scale01(climb['starvotes'])
    climb['scaledStaraverage'] = scale01(climb['staraverage'])

    # cast grade strings as float
    climb['rateFloatHueco'] = map(convert_string_grade, climb['rateHueco'])
    climb['rateFloatYDS'] = map(convert_string_grade, climb['rateYDS'])
    climb['ratePCTHueco'] = scale01(climb['rateFloatHueco'])
    climb['ratePCTYDS'] = scale01(climb['rateFloatYDS'])
    # combine YDS and Hueco grades
    # allows empirical comparison of Bouldering and Sport/Trad routes
    # not many conflicting cases -- max is reasonable assuption
    climb['grade'] = climb[['ratePCTHueco','ratePCTYDS']].max(axis='columns')

    return climb
