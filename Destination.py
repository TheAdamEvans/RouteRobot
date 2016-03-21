import re

class Destination(object):

    def __init__(self, href, feature):
        self.href = href

        # informal name for this destination
        pattern = re.compile('[\W_]+')
        word_only = pattern.sub('', href)
        self.nickname = word_only[1:-9]

        # initialize self with dictionary of features
        for n, feat in feature.items():
            setattr(self, n, feat)

    def update_feature():

        # update self new dictionary
        for n, feat in feature.items():
            setattr(self, n, feat)
