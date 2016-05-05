import pickle
import pandas as pd

import obj_scrape
import save_better as sb

ROOT_HREF = ''
DATA_DIR = './test_data/'
VOCAB = 'bigram_vocab.txt'
SAVE_AS = 'climb'
SCHEMA = [
    'href','nickname','starvotes','staraverage','is_area','is_route','single_climb_type',
    'commitment','protect_rate','feet','pitches','fa','elevation','season',
    'rateBritish','rateEwbanks','rateFont','rateFrench','rateHueco','rateUIAA','rateYDS','rateZA',
    'gps_coord','gps_coord_inferred','latitude','longitude',
    'mixed','ice','tr','boulder','aid','alpine','trad','sport','chipped',
    'page_views','img_height','img_src','img_width',
    'scaledFeet','scaledPitches','scaledStarvotes','scaledStaraverage',
    'rateFloatHueco','rateFloatYDS','ratePCTHueco','ratePCTYDS','grade',
    'tree_depth','num_children','state_name','parent_href','parent_name','parent_keyword',
    'name','keyword'
]

if __name__ == '__main__':

    # print "Scraping..."
    # obj_scrape.scrape_all(ROOT_HREF, DATA_DIR)
    
    print "Casting..."
    climb = sb.cast_all_pickles(DATA_DIR)

    print 'Vectorizing...'
    vocab = pd.read_csv(VOCAB, header=None)[0].tolist()
    X = sb.get_sparse_X(climb['description'], vocab)

    print 'Processing tokens...'
    climb['sparse_tfidf'] = pd.Series([X[i] for i in range(X.shape[0])], index=climb.index)
    climb['tokens'] = map(lambda row: sb.get_tokens(row, vocab), X)
    climb['keyword'] = sb.get_keyword(climb, 'tokens')

    print 'Collapsing hierarchy...'
    climb = sb.collapse_hierarchy(climb)

    print "Saving climb dataframe..."
    # save entire object as pickle
    climb.to_pickle(DATA_DIR + '_' + SAVE_AS)
    print "Wrote _%s to %s" % (SAVE_AS, DATA_DIR)
    # only save database-friendly columns
    climb[SCHEMA].to_csv(DATA_DIR + SAVE_AS + '.csv')
    print "Wrote %s.csv to %s" % (SAVE_AS, DATA_DIR)
