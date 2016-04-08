import pickle
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from Corpus import PrepareCorpus
from Corpus import HowSimilar
from Grade import PrepareGrade
from Grade import GradeSimilar

DATA_DIR = 'utah_data/'


print 'Reading climb dataframe pickle from ' + DATA_DIR
## SWAP OUT FOR FULL DATA
climb = pd.read_pickle(DATA_DIR + '_climb_no_children')
print "Shape of climb dataframe is", climb.shape

href = '/v/pocket-rocket/106297965'
# TODO check if href in climb

# create grade matrix
pipeline_grade = Pipeline([
    ('cast', PrepareGrade()),
    ('grading', GradeSimilar(href=href, climb_index=climb.index))
])

# create similarity matrix of climbs based on text similarity
pipeline_sim = Pipeline([
    ('preprocess', PrepareCorpus()),
    ('tfidf', TfidfVectorizer(
        decode_error='ignore', stop_words='english',
        sublinear_tf=True, ngram_range=(1, 1))),
    ('svd', TruncatedSVD(
        n_components=50, random_state=42)),
    ('similarity', HowSimilar(href=href, climb_index=climb.index))
])

FIT = pipeline_grade.fit(climb)
grade_scores = FIT.transform(climb)

FIT = pipeline_sim.fit(climb)
sim = FIT.transform(climb)

print "SIM is", sim.shape, type(sim)

# combine
recco = pd.concat([sim, grade_scores], axis=1)
recco['overall'] = recco['sim'] + recco['grade_score'] / 2 # BULLSHIT
recco.sort_values('overall', inplace=True, ascending=False)

print href
print recco[['sim', 'grade_score']][1:50]
