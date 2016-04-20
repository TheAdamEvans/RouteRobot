import pandas as pd
import cleaner as cl
from Destination import Destination

from statsmodels.distributions.empirical_distribution import ECDF

def find_id(href):
    return re.search(r'(\d+)$',href).group(1)

def scale01(feature):
    # always use on an entire column
    ecdf = ECDF(feature.dropna())
    qtile = ecdf(feature)
    scaled_feature = pd.Series(qtile, index=feature.index)
    
    # ECDF says NaN is 1.0
    scaled_feature[pd.isnull(feature)] = float('NaN')
    
    return scaled_feature

climb = pd.read_pickle('_climb_dataframe')
print "Shape of climb dataframe is", climb.shape

# get rid of destination object
del climb['children']

#climb['href_id'] = map(find_id, climb.index)

# allows mixing of Bouldering and Sport/Trad routes
climb['floatHueco'] = map(cl.convert_hueco, climb['rateHueco'])
climb['pctHueco'] = scale01(climb['floatHueco'])

climb['floatYDS'] = map(cl.convert_hueco, climb['rateYDS'])
climb['pctYDS'] = scale01(climb['floatYDS'])

# not many conflicting cases -- max is reasonable assuption
climb['gradeComb'] = climb[['pctHueco','pctYDS']].max(axis='columns')

climb.to_csv('_climb')