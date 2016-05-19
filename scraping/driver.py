import pickle
import pandas as pd

# from obj_scrape import scrape_all
from save_better import cast_all_pickles

ROOT_HREF = ''
DATA_DIR = './data/'


if __name__ == '__main__':

    # print 'Scraping...'
    # scrape_all(ROOT_HREF, DATA_DIR)
    
    print 'Casting...'
    climb = cast_all_pickles(DATA_DIR)
    climb.to_pickle(DATA_DIR+'climb_cast')
    print 'Saved '+DATA_DIR+'climb_cast'
