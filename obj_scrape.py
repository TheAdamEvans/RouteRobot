import os
from Scraper import Scraper
import json
import pickle

ROOT_HREF = '/v/'
DATA_DIR = './data/'

def traverse(node):

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
        print dest.href
        children.append(dest)

    node.children = children
    return node


if __name__ == '__main__':

    scrap = Scraper(ROOT_HREF)
    
    # iterate through areas immediately below
    for state_href in scrap.get_children():

        # initialize root destination with children
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

            # traverse tree of areas and routes
            all_dest = traverse(dest)
            # returns destination object

            # write out to file.. for viz??
            # BIG_JSON = DATA_DIR + dest.nickname + '.json'
            # with open(BIG_JSON, 'w+') as dump:
            #     flat = json.dumps(all_dest, default=lambda o: o.__dict__)
            #     dump.write(flat)

            # save destination object as pickle
            BIG_PICKLE = DATA_DIR + dest.nickname + '.pickle'
            with open(BIG_PICKLE, 'wb') as handle:
                pickle.dump(all_dest, handle)

            flourish = "<--------"
            print flourish + dest.nickname + flourish[::-1]

