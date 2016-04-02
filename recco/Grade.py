from time import time
import pandas as pd
import numpy as np
import re

from sklearn.base import BaseEstimator

from statsmodels.distributions.empirical_distribution import ECDF


class PrepareGrade(BaseEstimator):
    """ Get float difficulty for each climb """
    
    def __init__(self):
        return None

    def fit(self, climb, y=None):
        return self

    def transform(self, climb):
        
        climb['floatHueco'] = map(self.convert_hueco, climb['rateHueco'])
        climb['pctHueco'] = self.scale01(climb['floatHueco'])
        
        climb['floatZA'] = map(self.convert_ZA, climb['rateZA'])
        climb['pctZA'] = self.scale01(climb['floatZA'])
        
        # might prefer the YDS-esque rating if there is one
        # not many conflicting cases -- max is reasonable assuption
        climb['gradeComb'] = climb[['pctHueco','pctZA']].max(axis='columns')
        # print 'took %0.2f seconds' % (time() - t0)

        return climb
    
    def scale01(self, feature):
        # always use on an entire column
        na_pos = pd.isnull(feature)
        ecdf = ECDF(feature.dropna())
        qtile = ecdf(feature)
        qtile[na_pos] = float('NaN')
        return qtile

    def convert_ZA(self, ZA):
        if not pd.isnull(ZA):
            return float(ZA)
    
    def convert_hueco(self, hueco, LEAST_DIFFICULT=float(0), FIRST_STEP=float(1)):
    	# V0 --> 1.0
    	# V8 --> 9.0
    	# V3+ --> 4.5
    	# V4-5 --> 5.5

        if not pd.isnull(hueco):
            hueco = hueco[1:]
    
            if hueco == '-easy':
                # lower bound
                hard = LEAST_DIFFICULT
            else:
                # V0 will be equal to this
                hard = LEAST_DIFFICULT + FIRST_STEP
    
                # deal with the numbers in the string
                if re.search(r'(\+$)|(-$)', hueco):
                    pnt = float(hueco[:-1].strip())
                    # add/take a half a point off for plus minus
                    if hueco[-1] == '+':
                        hard += pnt + .5
                    else:
                        hard += pnt - .5
                elif re.search(r'(\d+)[- ]+(\d+)', hueco):
                    # return the mean of a range
                    lower = re.findall(r'\d+', hueco)[0].strip()
                    upper = re.findall(r'\d+', hueco)[1].strip()
                    hard += np.mean( [float(lower), float(upper)] )
                elif re.search(r'\d+', hueco):                    
                    try:
                        # cast as float ignoring sign
                        core_rate = float(hueco.strip('+-'))
                    except:
                        hard = None
                    else:
                        hard += core_rate
    
            return hard


class GradeSimilar(BaseEstimator):

    def __init__(self, href, climb_index):
        self.href = href
        self.climb_index = climb_index
        return None

    def fit(self, climb, y=None):
        return self

    def transform(self, climb):
        print 'Generating grade similarity...'

        # grab the grade we want to center around
        ideal_grade = climb['gradeComb'][climb.index == self.href][0]
        print ideal_grade, type(ideal_grade)

        # score each grade relative to ideal grade
        scores = [self.score_climb_grade(g, ideal_grade) for g in climb['gradeComb']]
        grade_score = pd.DataFrame( { 'grade_score': scores }, index=climb.index)
        return grade_score

    def score_climb_grade(self, grade, ideal_grade):

        ABOVE_DECAY = 5
        BELOW_DECAY = 2.5
        if not pd.isnull(grade):
            if grade == ideal_grade:
                return 1.0
            elif grade > ideal_grade:
                diff = grade - ideal_grade
                return (1-diff) ** ABOVE_DECAY
            else:
                diff = ideal_grade - grade
                return (1-diff) ** BELOW_DECAY
        else:
            return float('NaN')