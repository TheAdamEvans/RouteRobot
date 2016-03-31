from time import time
import pandas as pd

from sklearn.base import BaseEstimator
from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.metrics.pairwise import linear_kernel

class PrepareCorpus(BaseEstimator):

    def __init__(self):
        return None

    def fit(self, climb, y=None):
        return self

    def transform(self, climb):
        descriptive = self.get_total_climb_description(climb)
        return descriptive

    def combine_text(self, jess):
        
        # TODO do this with a map
        txt_collect = []
        for txt in ['description', 'other_text']:
            if hasattr(jess, txt):
                if not pd.isnull(jess[txt]):
                    txt_collect.append(jess[txt])
        
        return "\n".join(txt_collect)

    def get_total_climb_description(self, climb):
        collect = []
        for href, cmb in climb.iterrows():
            cmbtxt = self.combine_text(cmb)
            collect.append(cmbtxt)

        print "Combined text from %d rows" % len(collect)
        return collect


class HowSimilar(BaseEstimator):

    def __init__(self, href, climb_index):
        self.href = href
        self.climb_index = climb_index
        return None

    def fit(self, shrunk, y=None):
        # calculate cosines
        t0 = time()
        pos = self.climb_index == self.href
        sim = cosine_similarity(shrunk[pos], shrunk)
        self.sim = pd.DataFrame(sim[0], index=self.climb_index)
        self.sim.columns = ['sim']
        print 'Similarity matrix took %0.1f seconds' % (time()-t0)
        return self

    def transform(self, shrunk):
        return self.sim
