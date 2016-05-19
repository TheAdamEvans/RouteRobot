import pickle
import pandas as pd
from shutil import rmtree, copytree, copyfile

from text_mining import process_tokens, combine_dense_matrix
from collapse import collapse_hierarchy
from create_index import create_grade_map, cut_by_votes, index_features

DATA_DIR = './data/'
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

    # copy casted data over from scraping folder
    copytree('../scraping/'+DATA_DIR, DATA_DIR)
    copyfile(VOCAB, DATA_DIR+VOCAB)
    climb = pickle.load(open(DATA_DIR+'climb_cast'))

    print 'Vectorizing...'
    vocab = pd.read_csv(DATA_DIR+VOCAB, header=None)[0].tolist()
    # get IDF for arbitrary text queries later
    climb, idf_lookup, svd_comp = process_tokens(climb, vocab)
    pickle.dump(idf_lookup, open(DATA_DIR+'idf', 'wb'))
    pickle.dump(svd_comp, open(DATA_DIR+'svd_comp', 'wb'))
    
    print 'Collapsing hierarchy...'
    climb = collapse_hierarchy(climb)
    
    print 'Combining route and area descriptions...'
    climb['combined_dense_tfidf'] = combine_dense_matrix(climb)
    
    print 'Mapping grades...'
    grade_map = create_grade_map(climb, rating_system = ['rateHueco','rateYDS'])
    pickle.dump(grade_map, open(DATA_DIR+'grade_map', 'wb'))
    
    print 'Saving full data...'
    # save entire object before we start filtering
    climb.to_pickle(DATA_DIR+'_climb')
    
    print 'Indexing...'
    shorty = cut_by_votes(climb)
    type_index, state_index, word_index = index_features(shorty, vocab)
    slim = shorty[SCHEMA+['combined_dense_tfidf']].to_pickle(DATA_DIR+'climb')
    pickle.dump(type_index, open(DATA_DIR+'type_index','wb'))
    pickle.dump(state_index, open(DATA_DIR+'state_index','wb'))
    pickle.dump(word_index, open(DATA_DIR+'word_index','wb'))
    
    print 'Saving small data...'
    # save database-friendly only columns to csv
    climb[SCHEMA].to_csv(DATA_DIR+'climb.csv', header=True, index=None)
    for web_file in [VOCAB,'idf','grade_map','climb','state_index','word_index','type_index','svd_comp']:
        copyfile(DATA_DIR+web_file, '../../route-web/data/'+web_file)
