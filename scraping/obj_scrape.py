import os
import json
import pickle
from scraper import Scraper

def traverse(node):
    """ Pre-order depth-first search of Mountain Project tree """

    children = []
    for href in node.children_href:
        # initialize Scraper for this page
        scrap = Scraper(href)
        # grab features from the soup
        dest = scrap.create_destination()
        # find children in the soup if any
        dest.children_href = scrap.get_children()
        # recursively deeper down the tree if this is an area
        if dest.children_href != None:
            traverse(dest)
        # inner traverse function has returned with destination object
        print dest.nickname + ' | ' + dest.href
        children.append(dest)

    node.children = children
    return node


def scrape_all(ROOT_HREF, DATA_DIR):
    """ Scrape Mountain Project and save Destination objects """
    
    # iterate over children of the root (e.g. states in the US)
    scrap = Scraper(ROOT_HREF)
    for state_href in scrap.get_children():

        # initialize child destination
        scrap = Scraper(state_href)
        dest = scrap.create_destination()
        dest.children_href = scrap.get_children()

        # check if we have already crawled this area
        OBJECT_OUTFILE = DATA_DIR + dest.nickname + '.pickle'
        if os.path.exists(OBJECT_OUTFILE):
            print dest.nickname + ' has already been crawled'
            pass
        else:
            if not os.path.isdir(os.path.dirname(OBJECT_OUTFILE)):
                os.makedirs(os.path.dirname(OBJECT_OUTFILE))

            # traverse tree of areas-->routes
            all_dest = traverse(dest)
            # returns destination object

            # write out to file.. for viz??
            BIG_JSON = DATA_DIR + dest.nickname + '.json'
            with open(BIG_JSON, 'w+') as dump:
                flat = json.dumps(all_dest, default=lambda o: o.__dict__)
                dump.write(flat)

            # save destination object as pickle
            BIG_PICKLE = DATA_DIR + dest.nickname + '.pickle'
            with open(BIG_PICKLE, 'wb') as handle:
                pickle.dump(all_dest, handle)

            flourish = '<<<'+'-'*25
            print flourish + dest.nickname + flourish[::-1]
            print
