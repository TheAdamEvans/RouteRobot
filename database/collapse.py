import pandas as pd
from text_mining import get_keyword

def get_parent_datum(climb, col, depth=2):
    """ Lookup information from areas with specified depth
    Parents have depth -2 because self.href is last
    """
    collect = []
    for cmb in climb['href']:
        parent_href = climb.loc[cmb]['hierarchy']
        if len(parent_href) < depth:
            pdatum = float('NaN')
        else:
            pdatum = climb.loc[parent_href][col][-depth]
        collect.append(pdatum)
    return pd.Series(collect, index=climb.index)


def collapse_hierarchy(climb):
    """ Leverage then delete hierarchy, children_href """

    # quick counts for posterity
    climb['tree_depth'] = map(len, climb['hierarchy'])
    climb['num_children'] = map(lambda c: len(c) if isinstance(c,list) else 0, climb['children_href'])

    # what state is this climb in
    climb['state_name'] = get_parent_datum(climb, 'name', depth=0)

    # grab info from immediate parents
    # bunches of ways to make this faster
    climb['parent_href'] = get_parent_datum(climb, 'href')
    climb['parent_name'] = get_parent_datum(climb, 'name')
    climb['parent_tokens'] = get_parent_datum(climb, 'tokens')
    climb['parent_keyword'] = map(lambda t: get_keyword(t), climb['parent_tokens'])
    
    # parent vector is useful for recommendations
    climb['parent_sparse_tfidf'] = get_parent_datum(climb, 'sparse_tfidf')
    climb['parent_dense_tfidf'] = get_parent_datum(climb, 'dense_tfidf')
    
    # TODO collapse children
    # sum of starvotes, average staraverage, etc.

    return climb
