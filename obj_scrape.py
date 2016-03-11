from Scraper import Scraper
from Destination import Destination

def traverse(node):
    children = []
    for href in node.children_href:
        scrap = Scraper(href)
        dest = scrap.create_destination()
        dest.children_href = scrap.get_children()
        if dest.children_href != None:
            traverse_routes(dest)
        children.append(dest)
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