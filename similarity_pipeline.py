from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

import flatten as fat
from Corpus import PrepareCorpus
from Corpus import HowSimilar


DATA_DIR = './utah_data/'

print 'Reading pickles..'
climb = fat.combine_pickle(DATA_DIR)
print "Shape of climb dataframe is", climb.shape


# create similarity matrix of climbs based on text similarity
pipeline = Pipeline([
	('preprocess', PrepareCorpus()),
    ('tfidf', TfidfVectorizer(
    	decode_error='ignore', stop_words='english',
    	sublinear_tf=True, ngram_range=(1, 1))),
    ('svd', TruncatedSVD(
    	n_components=100, random_state=42)),
    ('similarity', HowSimilar())
])

FIT = pipeline.fit(climb)
sim = FIT.transform(climb)

print "SIM is", sim.shape, type(sim)