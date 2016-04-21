import re
import souper as sr
from urllib2 import urlopen
from bs4 import BeautifulSoup
from destination import Destination

class Scraper(object):
    """
    Scraper extracts information from mountain project page
    Heavy use of BeautifulSoup to navigate html tree
    Creates a Destination object
    """

    def __init__(self, href):
        self.href = href
        try:
            mp_page = urlopen('http://www.mountainproject.com/v/' + href)
        except:
            print href + ' failed to LOAD!'
            self.soup = None
        else:
            try:
                mp_html = mp_page.read()
            except:
                print href + ' failed to READ!'
                self.soup = None
            else:
                self.soup = BeautifulSoup(mp_html, 'html.parser')

    def get_child_href(self, dest_iter):
    
        href = []
        for dest in dest_iter:
            if len(dest.get_text()) > 0: # children are labeled with text
                if dest.a != None: # sometimes <a> is within a <span>
                    dest = dest.a
                h = dest.get('href')
                h = h.encode('utf-8', errors = 'ignore')
                href.append(h)
        
        # only routes and areas have an href containing /v/
        href = [h for h in href if '/v/' in h]
        # use the digits at the end of the href as index
        # links like .../v/108452874 work just fine
        href = [sr.find_id(h) for h in href]

        return href

    def get_children(self):

        # every route and area page has this container
        youContainer = self.soup.find(id="youContainer")
        root = youContainer == None

        if root: # at /v/ or /destinations/
            # get tags for the 50 states and International
            dest_iter = self.soup.find_all('span', { 'class': "destArea" })
            # pull out href key
            children = self.get_child_href(dest_iter)
            return children
        else:
            is_route = re.search('You & This Route',youContainer.get_text()) != None
            is_area = re.search('You & This Area',youContainer.get_text()) != None

            if is_route:
                return None
            elif is_area:
                # get div for any area or route
                leftnavdiv = self.soup.find(id='viewerLeftNavColContent')
                dest_iter = leftnavdiv.find_all('a')

                # pull out href key
                children = self.get_child_href(dest_iter)

                return children

    def create_destination(self):

        if self.soup:
            # what type of destination is this?
            youContainer = self.soup.find(id="youContainer")
            is_area = re.search('You & This Area',youContainer.get_text()) != None
            is_route = re.search('You & This Route',youContainer.get_text()) != None

            if not is_area and not is_route:
                # this is /v/
                # not a place you can visit
                dest = None
            else:
                # grab features from html
                feature = sr.get_general(self.soup)
                dest = Destination(self.href, feature)
                dest.is_area = is_area
                dest.is_route = is_route

                # more scraping is necessary for routes
                if dest.is_route:
                    dest.update_feature(sr.get_grade(self.soup))
                    dest.update_feature(sr.get_protect_rate(self.soup))
                    dest.update_feature(sr.get_star_rating(self.soup))
                    dest.update_feature(sr.get_type(feature['type']))

            return dest
