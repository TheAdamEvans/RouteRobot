import os
import json
import codecs
import traverser as tv
import souper as sr

HREF_OUTFILE = './data/routes.txt'
DATA_DUMP = './data/info.txt'

if __name__ == '__main__':

    print 'Traversing MountainProject for routes'
    root = '/v/tahquitz--suicide-rocks/105788020'

    # keep track of routes already crawled
    if os.path.exists(HREF_OUTFILE):
        print 'Route file exists, exiting'
        sys.exit(0)
    else:
        if not os.path.isdir(os.path.dirname(HREF_OUTFILE)):
            os.makedirs(os.path.dirname(HREF_OUTFILE))

    # collect href of all child routes
    tv.traverse_routes(root, HREF_OUTFILE)

    # iterate through known routes and grab data
    with open(HREF_OUTFILE) as all_href:
        for href in all_href:
            href = href.rstrip()
            route_info = sr.get_route_info(href)
            with open(DATA_DUMP, 'a') as dump:
                dump.write(json.dumps(route_info)+'\n')