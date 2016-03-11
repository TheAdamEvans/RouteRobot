class Destination(object):

    def __init__(self, href, feature):
        self.href = href

        # initialize self with dictionary of features
        for n, feat in feature.items():
            setattr(self, n, feat)

    def update_feature():

        # update self new dictionary
        for n, feat in feature.items():
            setattr(self, n, feat)
