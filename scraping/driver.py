import obj_scrape
import save_better

ROOT_HREF = ''
DATA_DIR = './data/'
SAVE_AS = 'climb'

if __name__ == '__main__':

    print "Scraping..."
    # obj_scrape.scrape_all(ROOT_HREF, DATA_DIR)
    
    print "Casting.."
    climb = save_better.cast_all_pickles(DATA_DIR)

    print "Saving..."
    climb.to_pickle(DATA_DIR + '_' + SAVE_AS)
    print "Wrote _%s to %s" % (SAVE_AS, DATA_DIR)
    climb.to_csv(DATA_DIR + SAVE_AS + '.csv')
    print "Wrote %s.csv to %s" % (SAVE_AS, DATA_DIR)
