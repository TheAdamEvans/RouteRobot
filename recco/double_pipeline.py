import pickle
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import FeatureUnion

from Corpus import PrepareCorpus
from Corpus import HowSimilar
from Grade import PrepareGrade
from Grade import GradeSimilar

from sklearn.base import BaseEstimator

class Selector(BaseEstimator):
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]

class Scaler(BaseEstimator):
    """ Turn column into a 0 - 1 distribution """
    def __init__(self):
        return None

    def fit(self, score, y=None):
        return self

    def transform(self, score):
        scaled = self.scale01(score)
        return scaled

    def scale01(self, feature):
        # always use on an entire column
        na_pos = pd.isnull(feature)
        ecdf = ECDF(feature.dropna())
        qtile = ecdf(feature)
        qtile[na_pos] = float('NaN')
        return qtile


DATA_DIR = './utah_data/'


print 'Reading climb dataframe pickle from ' + DATA_DIR
climb = pd.read_pickle(DATA_DIR + '_climb_dataframe')
print 'Shape of climb dataframe is', climb.shape

href = '/v/pocket-rocket/106297965'
# TODO check if href in climb

# create grade matrix
pipeline = Pipeline([
    ('cast', PrepareGrade()),
    ('grading', GradeSimilar(href=href, climb_index=climb.index))
])

FIT = pipeline.fit(climb)
climb['grade_recco'] = FIT.transform(climb)
climb = climb.sort_values('grade_recco', ascending=False)


print climb[['rateYDS','floatZA','grade_recco']].head(20)

# 
# pipeline = Pipeline([
# 
#     ('preprocessing_grade', PrepareGrade()),
# 
#     # combine the features from different aspects of the climb
#     ('union', FeatureUnion(
#         transformer_list=[
# 
#             # grade climbs in comparison to this one
#             ('grade', Pipeline([
#                 ('grading', GradeSimilar(href=href, climb_index=climb.index)),
#                 ('scale', Scaler())
#             ])),
# 
#             # standard bag-of-words model for description text
#             ('description_similarity', Pipeline([
#                 ('corpus', PrepareCorpus()),
#                 ('tfidf', TfidfVectorizer(
#                     decode_error='ignore', stop_words='english',
#                     sublinear_tf=True, ngram_range=(1, 2))),
#                 ('svd', TruncatedSVD(
#                     n_components=100, random_state=42)),
#                 ('similarity', HowSimilar(href=href, climb_index=climb.index)),
#                 ('scale', Scaler())
#             ])),
# 
#         ],
# 
#         # weight components in FeatureUnion
#         transformer_weights={
#             'grade': 1,
#             'similarity': 1,
#         },
#     )),
# 
# #    # Use a SVC classifier on the combined features
# #    ('svc', SVC(kernel='linear')),
# ])
# 
# FIT = pipeline.fit(climb)
# recco = FIT.transform(climb)
# #recco.sort_values('overall', inplace=True, ascending=False)
# print recco[['sim', 'grade_score']][1:20]
# 
# 
# 
# # combine
# #recco = pd.concat([sim, grade_scores], axis=1)
# #recco['overall'] = recco['sim'] + recco['grade_score'] / 2 # BULLSHIT
# #recco.sort_values('overall', inplace=True, ascending=False)
# 
# print href
# print recco[['sim', 'grade_score']][1:50]
# 
# 
