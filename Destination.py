class Destination(object):

    def __init__(self, href, feature):
        self.href = href

        # initialize self with dictionary of features
        for k, v in feature.items():
            setattr(self, k, v)

    def update_feature(self, feature):

        # update self new dictionary
        for k, v in feature.items():
            setattr(self, k, v)
