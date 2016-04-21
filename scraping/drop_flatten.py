import os
import pickle
import pandas as pd

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
        climb.set_index(climb.href.values, inplace = True, verify_integrity = True)
        return climb

def combine_pickle(DATA_DIR):
    
    # TODO do this in fewer lines
    collect_climb = []
    for area in os.listdir(DATA_DIR):
        pkl = '.pickle'
        if area[-len(pkl):] != pkl:
            pass
        else:
            dest = pickle.load(open(DATA_DIR + area, 'rb'))        
            partial = climb_from_dest(dest)
            collect_climb.append(partial)
    
    climb = pd.concat(collect_climb)
    return climb