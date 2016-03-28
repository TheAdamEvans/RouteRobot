import pickle
import pandas as pd
import numpy as np
import os

DATA_DIR = './test_data/'

def grab_children(dest, collect):
    if hasattr(dest, 'children'):
        for child in dest.children:
            collect.append(child.__dict__)
            grab_children(child, collect)
    return collect

def climb_from_dest(dest):
    kidnapped = grab_children(dest, collect = []) # kidnapping jokes are not okay
    climb = pd.DataFrame.from_dict(kidnapped) # neither are dict jokes
    if max(climb.shape) > 0:
        climb.set_index(climb.href.values, inplace = True, verify_integrity = False)
        return climb

def combine_pickle(DATA_DIR):   
    collect_climb = []
    for area in os.listdir(DATA_DIR):
        if area[-len('.pickle'):] != '.pickle':
            pass
        else:
            dest = pickle.load(open(DATA_DIR + area, 'rb'))        
            partial = climb_from_dest(dest)
            collect_climb.append(partial)
    
    climb = pd.concat(collect_climb)
    return climb

# import sys
# pct_area = np.mean(climb['is_area'])
# pct_route = np.mean(climb['is_route'])
# if pct_area + pct_route < (1 - sys.float_info.epsilon):
#     print "One or more records WAS NEITHER ROUTE NOR AREA"

climb = combine_pickle(DATA_DIR)
print climb.iloc[0]



