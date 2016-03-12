from Scraper import Scraper
from Destination import Destination
import json

def traverse(node):
    children = []
    for href in node.children_href:

        # call for this page and store the soup
        scrap = Scraper(href)

        # parse relevant infomation from the page
        dest = scrap.create_destination()

        # look for children of this route
        dest.children_href = scrap.get_children()

        # recursively deeper down the tree
        if dest.children_href is not None:
            traverse(dest)
        else:
            # at the route level (leafs)
            print dest.href
            children.append(dest)

    # set the destination objects as children
    node.children = children

    return node

# initialize root destination with children
root_href = '/v/the-nut-tree-boulders/105734016'
scrap = Scraper(root_href)
dest = scrap.create_destination()
dest.children_href = scrap.get_children()

# traverse tree of areas and routes
all_dest = traverse(dest)
# returns Destination object

# write out to file
BIG_JSON = './mp_tree.json'
with open(BIG_JSON, 'a') as dump:
    flat = json.dumps(all_dest, default=lambda o: o.__dict__)
    dump.write(flat)

print "Printed " + BIG_JSON