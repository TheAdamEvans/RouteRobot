import pandas as pd


def create_grade_map(climb, rating_system = ['rateHueco','rateYDS']):
    """ Create map like { '5.10b': 0.5512... } 
    Critical for scoring new grade queries without ECDF
    """

    grade_map = {}
    for label in rating_system:
        grpd = climb.groupby(label)['grade'].mean()
        grade_map.update(dict(zip(grpd.index, grpd.ravel())))

    return grade_map


def index_by_word(climb, vocab):
    """ index by word for faster searching """
    word_index = {word: [] for word in vocab}
    for index, row in climb.iterrows():
        # tokens are already checked to be in the vocab
        total_token = row['tokens'] + row['parent_tokens']
        for word in total_token:
            # grow dictionary of indexes
            word_index[word].append(index)
    return word_index


def index_by_type(shorty):
    """ index by type so users can specify bouldering, alpine, aid, etc. """

    climb_type = shorty['single_climb_type'].dropna().unique()
    
    typ_index = {typ: [] for typ in climb_type}
    for index, row in shorty.iterrows():
        # sometimes this is nan
        typ = row['single_climb_type']
        if typ in climb_type:
            # grow dictionary of indexes
            typ_index[typ].append(index)
    return typ_index


def index_by_state(climb):
    """ Make filtering by state faster by indexing """

    # load state table (generated from statetable.com!)
    state_table = pd.read_csv('../database/state_table.csv', index_col=0)
    
    state_index = {}
    for state in state_table['abbreviation']:
        proper_state_name = state_table['name'][state_table['abbreviation'] == state].iloc[0]
        # conventiently matches mountain project's website convention of specifying states
        loc = climb.index[climb['state_name'] == proper_state_name]
        # grow dictionary of indexes
        state_index[state] = loc
    return state_index


def index_features(shorty, vocab):

    type_index = index_by_type(shorty)
    state_index = index_by_state(shorty)
    word_index = index_by_word(shorty, vocab)
    
    return type_index, state_index, word_index


def cut_by_votes(climb, vote_thresh = 3):
    
    # filter to routes only
    shorty = climb[climb.is_route]
    # sort by prior likelihood to recommend
    shorty = climb.sort_values(['starvotes','staraverage','feet','href'], ascending=False)
    # take only routes with significant votes
    shorty = shorty[shorty['starvotes'] >= vote_thresh]
    
    return shorty