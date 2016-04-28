import obj_scrape
import save_better

ROOT_HREF = '105734016'
DATA_DIR = './nut_data/'
SAVE_AS = 'climb'

if __name__ == '__main__':
    obj_scrape.scrape_all(ROOT_HREF, DATA_DIR)
    climb = save_better.cast_all_pickles(DATA_DIR)

    climb.to_pickle(DATA_DIR + '_' + SAVE_AS)
    print "Wrote %s to %s" % (SAVE_AS, DATA_DIR)

    climb.to_csv(DATA_DIR + SAVE_AS + '.csv')
    print "Wrote %s.csv to %s" % (SAVE_AS, DATA_DIR)
