import pandas as pd


def index_climbs_by_state(climb):
    """ Make filtering by state faster by pre-indexing """

    # load state table (generated from statetable.com!)
    state_table = pd.read_csv('state_table.csv', index_col=0)
    
    state_index = {}
    for state in state_table['abbreviation']:
        proper_state_name = state_table['name'][state_table['abbreviation'] == state].iloc[0]
        # conventiently matches mountain project's website convention of specifying states
        loc = climb['state_name'] == proper_state_name
        state_index[state] = loc
    return state_index


def cut_size(climb, SCHEMA, vote_thresh = 3):
    """ Needs to be as fast as possible on the web """
    # routes and select columns
    slim = climb[SCHEMA+['combined_sparse_tfidf']][climb.is_route]
    # sort by likelihood to recommend
    slim = slim.sort_values(['starvotes','staraverage','feet','href'], ascending=False)
    # take only routes with significant votes
    slim = slim[slim['starvotes'] >= vote_thresh]
    state_index = index_climbs_by_state(slim)

    return slim, state_index
