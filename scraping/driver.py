import csv
import pickle
import pandas as pd
from shutil import copyfile

# from obj_scrape import scrape_all
from grade_cleaner import create_grade_map
from save_better import cast_all_pickles
from text_mining import process_tokens, combine_matrix
from collapse import collapse_hierarchy
from create_index import cut_size

ROOT_HREF = ''
DATA_DIR = './test_data/'
VOCAB = 'vocab.txt'
STATE_TABLE = 'state_table.csv'

SCHEMA = [
    'href','dest_name','starvotes','staraverage','is_area','is_route','single_climb_type',
    'commitment','protect_rate','feet','pitches',
    'latitude','longitude',
    'rateHueco', 'rateFrench','rateYDS','grade',
    'mixed','ice','tr','boulder','aid','alpine','trad','sport','chipped',
    'img_height','img_src','img_width',
    'scaledFeet','scaledPitches','scaledStarvotes','scaledStaraverage',
    'state_name','parent_href','parent_name','parent_keyword',
    'nickname','keyword'
]

if __name__ == '__main__':

    # print 'Scraping...'
    # scrape_all(ROOT_HREF, DATA_DIR)
    
    print 'Casting...'
    copyfile(VOCAB, DATA_DIR+VOCAB)
    climb = cast_all_pickles(DATA_DIR)

    print 'Vectorizing...'
    vocab = pd.read_csv(DATA_DIR+VOCAB, header=None)[0].tolist()
    climb, idf_lookup = process_tokens(climb, vocab)
    # save IDF for arbitrary text queries later
    pickle.dump(idf_lookup, open(DATA_DIR+'idf', 'wb'))

    print 'Collapsing hierarchy...'
    climb = collapse_hierarchy(climb)
    
    print 'Combining route and area descriptions...'
    climb['combined_sparse_tfidf'] = climb.apply(combine_matrix, axis=1)
    
    print 'Mapping grades...'
    grade_map = create_grade_map(climb, rating_system = ['rateHueco','rateYDS'])
    pickle.dump(grade_map, open(DATA_DIR+'grade_map', 'wb'))

    print 'Saving data...'
    # save entire object
    climb.to_pickle(DATA_DIR+'_climb')

    # only [areas and most popular climbs, slim columns] + sparse description information
    slim, state_index = cut_size(climb, SCHEMA)
    slim.to_pickle(DATA_DIR+'climb')
    pickle.dump(state_index, open(DATA_DIR+'state_index','wb'))

    # save database-friendly only columns to csv
    climb[SCHEMA].to_csv(DATA_DIR+'climb.csv', header=True, index=None)

    for web_file in [VOCAB,'idf','grade_map','climb','state_index']:
        copyfile(DATA_DIR+web_file, '../../route-web/data/'+web_file)
