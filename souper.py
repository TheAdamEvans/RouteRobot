import urllib2
import re
from bs4 import NavigableString

GPSre = re.compile(r'(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)')
pitchRE = re.compile(r'^(\d)+ pitch')
feetRE = re.compile(r'^(\d)+\'')
commitmentRE = re.compile(r'Grade [VI]+')

def get_box_data(soup):

    # find stats box in soup with regex
    page_table = soup.find_all('table')
    for box in page_table:
        if re.search("Submitted By:",box.encode('utf-8')) != None: # TODO questionable logic
            break

    box_data = {}

    for tr in box.find_all('tr'):

        # encode html to scan with regex
        tr_str = tr.encode('utf-8', errors = 'ignore')

        # UTF-8 characters that separate data
        split_char = ':\xc2\xa0'

        # check if this table row one we want   
        permissable_datum = ['Location', 'Page Views', 'FA', 'Type', 'Elevation', 'Season', 'Submitted By']
        perRE = re.compile("|".join(permissable_datum))
        perMatch = perRE.search(tr_str)

        # if it is a permissable data row
        if perMatch != None:
            morsel = tr.get_text().encode('utf-8', errors = 'ignore')
            i = morsel.split(split_char)
            head = i[0].strip().replace(' ','_').lower()
            body = i[1].strip()

            # Location body has junk in it like "\xc2\xa0Incorrect?"
            GPSmatch = GPSre.search(body)
            if GPSmatch is not None:
                body = GPSmatch.group(0)

            # easier to cast as int later
            if head == 'page_views':
                body = body.replace(',','')

            # store data in dict
            box_data[head] = body

    return box_data

def get_protect_rate(soup):

    # up there with with route name
    grade_table = soup.h3
    
    # finds ratings like PG13, R, X, A1, etc.
    # destroys the grade spans and looks for text
    while grade_table.span != None:
        grade_table.span.decompose()
    protect_rate = grade_table.getText()
    protect_rate = protect_rate.encode('utf8', errors = 'ignore').strip()
    
    if protect_rate != "":
        return { 'protect_rate': protect_rate }

def get_area_hierarchy(soup):

   navboxdiv = soup.find(id="navBox").div
   href_list = navboxdiv.find_all('a')

   parent = []
   for h in href_list:
       p = h.get('href')
       p = p.encode('utf-8', errors = 'ignore')
       parent.append(p)

   return { 'area_hierarchy': parent }

def get_description(soup):

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

    if len(other_text) > 0:
        detail['other_text'] = '\n'.join(other_text)

    return detail

def get_route_name(soup):

    route_soup = soup.h1.get_text()
    route_name = route_soup.encode('utf-8' ,errors = 'ignore')
    route_name = route_name.strip('\xc2\xa0 ')

    return { 'name': route_name }

def get_star_rating(soup):
    
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
        h = g.split(':\xc2\xa0')
        if len(h) > 1:
            grade_data['rate'+h[0].strip()] = h[1]

    return grade_data

def get_type(cmb_type):

    kind_pitches_feet = str(cmb_type).split(', ')

    kind = {}
    for morsel in kind_pitches_feet:
        terminology = ['Boulder','Trad','Sport','TR','Aid','Ice','Mixed','Alpine','Chipped']
        if morsel in terminology:
            kind[morsel.lower()] = True
        elif pitchRE.search(morsel):
            kind['pitches'] = morsel.split(' ')[0]
        elif feetRE.search(morsel):
            kind['feet'] = float(morsel[:-1])
        elif commitmentRE.search(morsel):
            kind['commitment'] = morsel.split(' ')[-1]
    return kind

def get_general(soup):
    
    # call soup helper functions
    general_info = {}
    general_info.update(get_route_name(soup))
    general_info.update(get_box_data(soup))
    general_info.update(get_description(soup))
    general_info.update(get_area_hierarchy(soup))

    return general_info