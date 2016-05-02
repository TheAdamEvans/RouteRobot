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
        if scrap.soup is None:
            pass
        else:
            # grab features from the soup
            dest = scrap.create_destination()
            # find children in the soup if any
            dest.children_href = scrap.get_children()
            # recursively deeper down the tree if this is an area
            if dest.children_href != None:
                print
                print '**'+dest.nickname+'**'
                traverse(dest)
            # inner traverse function has returned with destination object
            print dest.nickname + ' | ' + dest.href
            children.append(dest)

    node.children = children
    return node

def save_info_from(href, data_dir):

    # initialize child destination
    scrap = Scraper(href)
    dest = scrap.create_destination()
    dest.children_href = scrap.get_children()

    # check if we have already crawled this area
    OBJECT_OUTFILE = data_dir + dest.nickname + '.pickle'
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
        BIG_JSON = data_dir + dest.nickname + '.json'
        with open(BIG_JSON, 'w+') as dump:
            flat = json.dumps(all_dest, default=lambda o: o.__dict__)
            dump.write(flat)

        # save destination object as pickle
        BIG_PICKLE = data_dir + dest.nickname + '.pickle'
        with open(BIG_PICKLE, 'wb') as handle:
            pickle.dump(all_dest, handle)

        flourish = '<<<'+'-'*25
        print flourish + dest.nickname + flourish[::-1]
        print


def scrape_all(root_href, data_dir):
    """ Scrape Mountain Project and save Destination objects """
    
    scrap = Scraper(root_href)

    # iterate over children of the root (e.g. states in the US)
    for href in scrap.get_children():
        save_info_from(href, data_dir)
