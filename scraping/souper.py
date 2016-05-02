import re
from bs4 import NavigableString

SPLIT_CHAR = ':\xc2\xa0'
idRE = re.compile(r'(\d+)$')
gpsRE = re.compile(r'(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)')
pitchRE = re.compile(r'^(\d)+ pitch')
feetRE = re.compile(r'^(\d)+\'')
commitmentRE = re.compile(r'Grade [VI]+')
nbspRE = re.compile(r'\xc2\xa0')
yearRE = re.compile(r'[0-9][0-9][0-9][0-9]')


def find_id(href):
    """ Extract numeric id from href """
    ID = idRE.search(href)
    if ID:
        return ID.group(1)


def get_first_img_source(soup):
    """ Get link and dimensions of first photo """

    d = {}
    img = soup.find('img', { 'class': "img-shadow" })
    if img is None:
        pass
    else:
        d['img_src'] = img['src']
        if img.has_attr('height'):
            d['img_height'] = img['height']
        if img.has_attr('width'):
            d['img_width'] = img['width']

    return d


def get_route_name(soup):
    """ Get huge text name at the top """

    route_soup = soup.h1
    route_name = route_soup.getText()
    route_name = route_name.encode('utf-8' ,errors = 'ignore')

    # get rid of \xc2\xa0Rock Climbing
    NBSP = nbspRE.search(route_name)
    if NBSP:
        route_name = route_name[:NBSP.start()]
    route_name = route_name.strip()

    return { 'name': route_name }


def get_box_data(soup):
    """ Finds upper box with all sorts of morsels of info and returns dictionary """
    
    permissable_datum = ['Location', 'Page Views', 'FA', 'Type', 'Elevation', 'Season', 'Submitted By']
        
    # find stats box in soup with regex
    page_table = soup.find_all('table')
    for box in page_table:
        if re.search('Submitted By:',box.encode('utf-8')) != None:
            # questionable logic here
            break

    box_data = {}
    for tr in box.find_all('tr'):
        # encode html to scan with regex
        tr_str = tr.encode('utf-8', errors = 'ignore')

        # regex for matching any of the labels
        perRE = re.compile('|'.join(permissable_datum))
        perMatch = perRE.search(tr_str)

        # if it is a permissable data row
        if perMatch != None:
            morsel = tr.get_text().encode('utf-8', errors = 'ignore')
            i = morsel.split(SPLIT_CHAR)
            head = i[0].strip().replace(' ','_').lower()
            body = i[1].strip()

            # easier to cast as int later
            if head in ['page_views','elevation']:
                body = body.replace(',','')

            # only return submitted year if there is one
            if head in ['fa','submitted_by']:
                yearMatch = yearRE.search(body)
                if yearMatch:
                    body = int(yearMatch.group(0))

            # isolate GPS coordinate string
            if head == 'location':
                # there is another column named location DOH!
                head = 'gps_coord'
                GPSmatch = gpsRE.search(body)
                if GPSmatch is None:
                    body = float('NaN')
                else:
                    body = GPSmatch.group(0)
                    
            # store data in dict
            box_data[head] = body

    return box_data

def get_description(soup):
    """ Grab text for use in analysis
    Lots of routes have descriptive entires with headers other than Description
    Choice here is to INCLUDE other text with Description
    """

    standard_head = ['Description', 'Getting There', 'Protection', 'Location']

    # grab all h3 orange header sections on the page
    detail = {}
    other_text = []
    for h3 in soup.find_all('h3', { 'class': "dkorange" }):
        
        # text is the element after the h3
        body = h3.next_sibling
        
        if isinstance(body, NavigableString):
            # ignore sections from here on like 'Climbing Season' and such
            break
        else:
            # these are the valuable text sections
            body = body.get_text()
            body = body.encode('utf-8', errors = 'ignore')
            head = h3.get_text().encode('utf-8', errors = 'ignore')
            head = head.strip('\xc2\xa0')

            if head in standard_head:
                head = head.replace(' ','_').lower()
                detail[head] = body
            else:
                other_text.append(body)

    # combine text into a full description
    if len(other_text) > 0:
        if 'description' in detail:
            # combine description with other text -- questionable but appropriate
            detail['description'] = detail['description'] + '\n'.join(other_text)
        else:
            detail['description'] = '\n'.join(other_text)

    # blank if there is no text at all
    if 'description' not in detail:
        detail['description'] = ''

    return detail

def get_protect_rate(soup):
    """ Finds protection rating (if there is one)
    like PG13, R, X, A1, etc. and returns dictionary """

    # up there with with route name
    grade_table = soup.h3
    
    # destroys the grade spans and looks for text
    while grade_table.span != None:
        grade_table.span.decompose()
    protect_rate = grade_table.getText()
    protect_rate = protect_rate.encode('utf8', errors = 'ignore').strip()
    
    return { 'protect_rate': protect_rate }


def get_area_hierarchy(soup):
    """ Returns list of parents all the way to the root """

    navboxdiv = soup.find(id="navBox").div
    href_list = navboxdiv.find_all('a')

    parent = []
    for h in href_list:
        p = h.get('href')
        p = p.encode('utf-8', errors = 'ignore')
        p = find_id(p)
        parent.append(p)

    # omit root from the hierarchy
    return { 'area_hierarchy': parent[1:] }


def get_star_rating(soup):
    """ find starvotes, staraverage """

    # starbest is totally unreliable
    # /v/religious-retreat/109207355 has a 1.0 rating = 'bomb'
    
    star_rating = {}
    if soup.find(id="starSummaryText") != None:
        meta = soup.find(id="starSummaryText").find_all('meta')
        for m in meta:
            head = m['itemprop']
            head = head.encode('utf-8', errors = 'ignore')
            body = m['content']
            body = body.encode('utf-8', errors = 'ignore')
            star_rating['star' + head] = body
            
        return star_rating


def get_grade(soup):
    """ Find consensus grade of this climb
    return dictionary with grade in multiple rating systems """

    # up there with with route name
    grade_table = soup.h3

    # look for grades in spans
    grade = []
    for s in grade_table.find_all('span'):

        # class names are the grading systems
        if s['class'] != None:
            head = s['class'][0]
            head = head.encode('utf8', errors = 'strict')

            # grade are showing with text
            body = s.get_text()
            body = body.encode('utf8', errors = 'ignore')

            grade.append(body)

    # extract tbe grades
    grade_data = {}
    for g in grade:
        h = g.split(SPLIT_CHAR)
        if len(h) > 1:
            grade_data['rate'+h[0].strip()] = h[1]

    return grade_data


def get_type(cmb_type):
    """ Get info about the type of climb, including pitches, feet, commitment rating
    Called from Scraper if is_route
    """

    terminology = ['Boulder','Trad','Sport','TR','Aid','Ice','Mixed','Alpine','Chipped']

    kind = {}
    kind_pitches_feet = str(cmb_type).split(', ')
    for morsel in kind_pitches_feet:
        if morsel in terminology:
            # columns end up either True or NaN
            kind[morsel.lower()] = True
        elif pitchRE.search(morsel):
            kind['pitches'] = morsel.split(' ')[0]
        elif feetRE.search(morsel):
            kind['feet'] = float(morsel[:-1])
        elif commitmentRE.search(morsel):
            kind['commitment'] = morsel.split(' ')[-1]
    return kind


def get_general(soup):
    """ Call soup helper functions and return dictionary with all features """
    
    general_info = {}
    general_info.update(get_route_name(soup))
    general_info.update(get_box_data(soup))
    general_info.update(get_description(soup))
    general_info.update(get_area_hierarchy(soup))
    general_info.update(get_first_img_source(soup))

    return general_info