import urllib2
import re
import bs4
import codecs

GPSre = re.compile('(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)')

def get_box_data(soup):

    # find stats box in soup with regex
    page_table = soup.find_all('table')
    for box in page_table:
        if re.search("Submitted By:",box.encode('utf-8')) != None: # questionable
            break

    box_data = {}

    for tr in box.find_all('tr'):

        # encode html to scan with regex
        tr_str = tr.encode('utf-8', errors = 'ignore')

        # UTF-8 characters that separate data
        split_char = ':\xc2\xa0'

        # check if this table row one we want
        permissable_datum = ['Location', 'Page Views', 'Administrators', 'Submitted By', 'FA', 'Type', 'Elevation']
        perRE = re.compile("|".join(permissable_datum))
        perMatch = perRE.search(tr_str)

        # if it is a permissable data row
        if perMatch != None:
            morsel = tr.get_text().encode('utf-8', errors = 'ignore')
            i = morsel.split(split_char)
            head = i[0].strip()
            body = i[1].strip()

            # Location body has junk in it like "\xc2\xa0View Map\xc2\xa0\xc2\xa0Incorrect?"
            GPSmatch = GPSre.search(body)
            if GPSmatch is not None:
                body = GPSmatch.group(0)

            # store data in dict
            box_data[head] = body

    return box_data


def get_protect_rate(soup):

    # up there with with route name
    grade_table = soup.h3
    
    # finds ratings like PG13, R, X
    # destroys the grade spans and looks for text
    while grade_table.span != None:
        grade_table.span.decompose()
    protect_rate = grade_table.getText()
    protect_rate = protect_rate.encode('utf8', errors = 'ignore').strip()
    
    return protect_rate


def get_area_hierarchy(soup):

   navboxdiv = soup.find(id="navBox").div
   href_list = navboxdiv.find_all('a')

   parent = []
   for h in href_list:
       p = h.get('href')
       p = p.encode('utf-8', errors = 'ignore')
       parent.append(p)

   return parent

def get_description(soup):

    detail = {}
    for h3 in soup.find_all('h3', { 'class': "dkorange" }):

        # encode html to scan with regex
        h3_str = h3.get_text().encode('utf-8', errors = 'ignore')

        # headers of info we want
        permissable_datum = ['Description', 'Getting There', 'Protection', 'Location']

        # see which one matches
        for head in permissable_datum:
            perMatch = re.search(head, h3_str)
            if perMatch != None:

                # text is the element after the h3
                body = h3.next_sibling

                # save text
                detail_str = body.get_text().encode('utf-8', errors = 'ignore')
                detail[head] = detail_str.strip()

    return detail


def get_route_name(soup):

    route_soup = soup.h1.get_text()
    
    route_name = route_soup.encode('utf-8' ,errors = 'ignore')

    route_name = route_name.strip('\xc2\xa0 ')

    return { 'Name': route_name }


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

    # format grade adding protection rating
    # grade = [(s + " " + protect_rate).strip() for s in grade]
    
    # extract tbe grades
    grade_data = {}
    for g in grade:
        h = g.split(':\xc2\xa0')
        if len(h) > 1:
            grade_data['rate'+h[0].strip()] = h[1]

    return grade_data


def get_route_info(soup):
        
    route_name = get_route_name(soup)
    box_data = get_box_data(soup)
    detail = get_description(soup)
    grade = get_grade(soup)
    protect_rate = get_protect_rate(soup)
    area_hierarchy = get_area_hierarchy(soup)

    route_info = {}
    route_info.update(route_name)
    route_info.update(box_data)
    route_info.update(detail)
    route_info.update(grade)

    # TODO protect rate should return None if nothing found (currently returns "")
    route_info['protect_rate'] = protect_rate

    route_info['area_hierarchy'] = area_hierarchy

    route_info = dict((k.lower(), v) for k,v in route_info.iteritems())
    
    for k, v in route_info.items():
        if k in ['Description', 'Getting There', 'Location']:
            pass
            # TODO return text as scipy sparse matrix

    

#        is_area = re.search('You & This Area',youContainer.get_text()) != None
#        if not is_area:
#            star_rating = get_star_rating(soup)
#            route_info.update(star_rating)


        
    return route_info