import urllib2
import re
import bs4

def get_children(href):

    try:
        mp_page = urllib2.urlopen('http://www.mountainproject.com' + href)
    except:
        return None
    else:
        mp_html = mp_page.read()
        soup = bs4.BeautifulSoup(mp_html, 'html.parser')

        # every route and area page has this container
        youContainer = soup.find(id="youContainer")
        root = youContainer == None

        if root: # at /v/ or /destinations/
            # get tags for the 50 states and International
            dest_iter = soup.find_all('span', { 'class': "destArea" })

            # pull out href key
            children = get_child_href(dest_iter)

            return children
        else:
            
            is_route = re.search('You & This Route',youContainer.get_text()) != None
            is_area = re.search('You & This Area',youContainer.get_text()) != None

            if is_route:
                return None
            elif is_area:
                # get div for any area or route
                leftnavdiv = soup.find(id='viewerLeftNavColContent')
                dest_iter = leftnavdiv.find_all('a')

                # pull out href key
                children = get_child_href(dest_iter)

                return children


def get_child_href(dest_iter):
    
    href = []
    
    for dest in dest_iter:
        if len(dest.get_text()) > 0: # children are labeled with text
            if dest.a != None: # sometimes <a> is within a <span>
                dest = dest.a
            h = dest.get('href')
            h = h.encode('utf-8', errors = 'ignore') # encoding is crucial
            href.append(h)
    
    # only routes and areas have an href containing /v/
    href = [h for h in href if '/v/' in h]
    
    return href


def traverse_routes(href, HREF_OUTFILE):

    children = get_children(href)

    for child in children:
        if get_children(child) != None:
            # recursively deeper into the rabbit hole
            traverse_routes(child, HREF_OUTFILE)
        else:
            with open(HREF_OUTFILE, 'a') as f:
                f.write(child+'\n')
                print child

    return children