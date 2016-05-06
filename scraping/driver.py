from shutil import copyfile
import pickle
import pandas as pd

import obj_scrape
from grade_cleaner import create_grade_map
from save_better import cast_all_pickles
from text_mining import process_tokens
from collapse import collapse_hierarchy

ROOT_HREF = ''
DATA_DIR = './test_data/'
VOCAB = 'vocab.txt'

SCHEMA = [
    'href','nickname','starvotes','staraverage','is_area','is_route','single_climb_type',
    'commitment','protect_rate','feet','pitches','elevation','season',
    'latitude','longitude',
    'rateBritish','rateEwbanks','rateFont','rateFrench','rateHueco','rateUIAA','rateYDS','rateZA',
    'mixed','ice','tr','boulder','aid','alpine','trad','sport','chipped',
    'page_views','img_height','img_src','img_width',
    'scaledFeet','scaledPitches','scaledStarvotes','scaledStaraverage',
    'rateFloatHueco','rateFloatYDS','ratePCTHueco','ratePCTYDS','grade',
    'tree_depth','num_children','state_name','parent_href','parent_name','parent_keyword',
    'name','keyword'
]

if __name__ == '__main__':

    # print 'Scraping...'
    # obj_scrape.scrape_all(ROOT_HREF, DATA_DIR)
    
    print 'Casting...'
    climb = cast_all_pickles(DATA_DIR)
    copyfile(VOCAB, DATA_DIR+VOCAB)

    print 'Vectorizing...'
    vocab = pd.read_csv(DATA_DIR+VOCAB, header=None)[0].tolist()
    climb, idf_lookup = process_tokens(climb, vocab)
    # save IDF for arbitrary text queries later
    pickle.dump(idf_lookup, open(DATA_DIR+'idf', 'wb'))

    print 'Collapsing hierarchy...'
    climb = collapse_hierarchy(climb)

    print 'Mapping grades...'
    grade_map = create_grade_map(climb, rating_system = ['rateHueco','rateYDS'])
    pickle.dump(grade_map, open(DATA_DIR+'grade_map', 'wb'))

    print 'Saving data...'
    # save entire object
    climb.to_pickle(DATA_DIR+'_climb')
    # slim columns + sparse description information
    climb[SCHEMA+['sparse_tfidf','parent_sparse_tfidf']].to_pickle(DATA_DIR+'climb')
    # save database-friendly only columns to csv
    climb[SCHEMA].to_csv(DATA_DIR+'climb.csv', header=True, index=None)

    for web_file in [VOCAB,'idf','grade_map','climb']:
        print 'Copied to route-web/data/'+web_file
        copyfile(DATA_DIR+web_file, '../../route-web/data/'+web_file)
