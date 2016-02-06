import re
import urllib2
import sys
import bs4
import codecs
import warnings


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
            else:
                warnings.warn("NEITHER ROUTE NOR AREA " + href)


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
            
            # body has junk in it like "\xc2\xa0View Map\xc2\xa0\xc2\xa0Incorrect?"
            # store data in dict
            box_data[head] = body

    return box_data


def get_protect_rate(grade_table):
    
    # finds ratings like PG13, R, X
    # destroys the grade spans and looks for text
    while grade_table.span != None:
        grade_table.span.decompose()
    protect_rate = grade_table.getText()
    protect_rate = protect_rate.encode('utf8', errors = 'ignore').strip()
    
    return protect_rate


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

    # get protection aka scary rating
    if grade_table != None:
        while grade_table.span != None:
            grade_table.span.decompose()
        protect_rate = grade_table.getText()
        protect_rate = protect_rate.encode('utf8', errors = 'ignore').strip()
    else:
        protect_rate = ''

    # format grade adding protection rating
    grade = [(s + " " + protect_rate).strip() for s in grade]

    grade_data = {}
    
    # extract tbe grades
    for g in grade:
        h = g.split(':\xc2\xa0')
        if len(h) > 1:
            grade_data['rate'+h[0].strip()] = h[1]

    return grade_data


def get_route_info(href):
    
    try:
        mp_page = urllib2.urlopen('http://www.mountainproject.com' + href)
    except:
        return None
    else:
        mp_html = mp_page.read()
        soup = bs4.BeautifulSoup(mp_html, 'html.parser')
        
        route_name = get_route_name(soup)
        box_data = get_box_data(soup)
        star_rating = get_star_rating(soup)
        detail = get_description(soup)
        grade = get_grade(soup)
        
        route_info = {}
        route_info.update(route_name)
        route_info.update(box_data)        
        route_info.update(star_rating)
        route_info.update(detail)
        route_info.update(grade)
        
        return route_info


def print_dict(child_detail):
    for datum in child_detail:
        fd = codecs.open("data/"+datum,'a', 'utf-8')
        d = child_detail[datum].decode('utf-8', errors = 'ignore')
        fd.write(d)
        fd.write("\n\n")
        fd.close()


def traverse(href):
    print href
    children = get_children(href)
    for child in children:
        if get_children(child) != None:

            # recursively deeper into the rabbit hole
            traverse(child)
        else:
            for child in children:

                # print data from route
                child_detail = get_route_info(child)
                if child_detail != None:
                    print child_detail['Name']
                    print_dict(child_detail)
            return child

traverse('/v/')
