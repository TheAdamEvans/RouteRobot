import pickle
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

import flatten as fat
from Corpus import PrepareCorpus
from Corpus import HowSimilar
from Grade import PrepareGrade
from Grade import GradeSimilar


DATA_DIR = './utah_data/'

print 'Reading pickles..'
climb = fat.combine_pickle(DATA_DIR)
climb = climb.head(1000)
print "Shape of climb dataframe is", climb.shape
climb.to_pickle(DATA_DIR + '_climb_dataframe')

href = climb['href'][-10]

# create grade matrix
pipeline = Pipeline([
    ('cast', PrepareGrade()),
    ('grading', GradeSimilar())
])

FIT = pipeline.fit(climb)
grade_scores = FIT.transform(climb)

print "Grade scores are", grade_scores.shape, type(grade_scores)

grade_scores = pd.DataFrame(grade_scores, index=climb.index, columns=climb.index)
grade_scores.to_pickle(DATA_DIR + '_grade_matrix')

x = pd.read_pickle(DATA_DIR + '_grade_matrix')
print "Grades are", x.shape, type(x)

# create similarity matrix of climbs based on text similarity
pipeline = Pipeline([
    ('preprocess', PrepareCorpus()),
    ('tfidf', TfidfVectorizer(
        decode_error='ignore', stop_words='english',
        sublinear_tf=True, ngram_range=(1, 2))),
    ('svd', TruncatedSVD(
        n_components=100, random_state=42)),
    ('similarity', HowSimilar(href=href, climb_index=climb.index))
])

FIT = pipeline.fit(climb)
sim = FIT.transform(climb)

print "SIM is", sim.shape, type(sim)

sim.to_pickle(DATA_DIR + '_similarity_matrix')
x = pd.read_pickle(DATA_DIR + '_similarity_matrix')
print "SIM is", x.shape, type(x)
print sim
