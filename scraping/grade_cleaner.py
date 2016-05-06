import re
import numpy as np
import pandas as pd

def convert_string_grade(grd, LEAST_DIFFICULT=float(0), FIRST_STEP=float(1)):
    """ Takes string grade and converts it to a float """

    if not pd.isnull(grd):
        # trim the prefix before the core grade
        pre = 0
        if re.search(r'^V', grd):
            pre = 1
        elif re.search(r'^5\.', grd):
            pre = 2
        grd = grd[pre:]
        
        # some special easy cases
        if grd in ['-easy', '3rd', '4th', 'Easy 5th']:
            # lower bound
            hard = LEAST_DIFFICULT
        else:
            # V0 will be equal to this
            hard = LEAST_DIFFICULT + FIRST_STEP
            # factor in the +/- or abcd
            hard += cast_grade(grd)
            
        return hard


def cast_grade(grd):
    """ Deals with grades with endings like abcd and +/- """
    
    # abcd grades YDS grades fall here
    if re.search(r'[abcd]$', grd):
        pnt = float(grd.strip('abcd/'))
        adj = adj_from_letter(grd)
        rate = pnt + adj
    
    # anything ending in +/-
    elif re.search(r'(\+$)|(-$)', grd):
        pnt = float(grd[:-1].strip())
        # add/take a half a point off for plus minus
        if grd[-1] == '+':
            rate = pnt + .5
        else:
            rate = pnt - .5
    
    # grd ratings often have a range like V3-4
    elif re.search(r'(\d+)[- ]+(\d+)', grd):
        # return the mean of range
        lower = re.findall(r'\d+', grd)[0].strip()
        upper = re.findall(r'\d+', grd)[1].strip()
        rate = np.mean( [float(lower), float(upper)] )
    
    # if we can find any number cast as float ignoring sign
    elif re.search(r'\d+', grd):
        try:
            core_rate = float(grd.strip('+-/'))
        except:
            rate = None
        else:
            rate = core_rate
    
    else:
        rate = None

    return rate


def adj_from_letter(grade):
    """ Translate letter suffix into a number """

    letter_jumble = re.sub('[\W\d_]+', '', grade)
    
    adj = []
    for letter in letter_jumble:
        if letter == 'a':
            adj.append(-.5)
        elif letter == 'b':
            adj.append(-.25)
        elif letter == 'c':
            adj.append(+.25)
        elif letter == 'd':
            adj.append(+.5)
            
    # mean not sum beacuse b/c is easier than c
    return np.mean(adj)


#def map_grades(climb):
#    grpd = climb.groupby(by=['rateHueco'])
#    grade = grpd.mean()
    #
#    return dict(zip(hueco, grade))