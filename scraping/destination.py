import re

class Destination(object):
    """ Abstraction of routes and areas """

    def __init__(self, href, feature):
        self.href = href

        # initialize self with dictionary of features
        for n, feat in feature.items():
            setattr(self, n, feat)

        # having a nickname is nice
        if self.name:
            self.nickname = ''.join(re.findall("[a-zA-Z]+", self.name)).lower()
        else:
            self.nickname = self.href


    def update_feature(self, feature):
        if feature:
            for n, feat in feature.items():
                setattr(self, n, feat)
