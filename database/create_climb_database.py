import sqlite3
import pandas as pd

import measure as meas

DB = 'climbon.db'

def insert_recco(conn, href, climb, FIT, top=10):
    
    # get recommendation
    top_recco = meas.give_recommendation(FIT, href, top)

    # keep track of what route is being recommended
    o = {'origin_id': href }
    origin = pd.DataFrame(o, index=top_recco.index)
    
    # subset the climb info and recco scores
    # must match schema.sql
    scores = top_recco[['description','grade','staraverage','best']]
    info = climb[['href','name','rateYDS','feet','keyword']]
    jnd = pd.concat([origin, info, scores], axis=1, join='inner')
    
    # replace float('NaN') with None to play nicely with sqlite3
    jnd = jnd.where((pd.notnull(jnd)), None)
    
    # run many insert statements
    jnd.to_sql('climb', conn, if_exists='append', index=False)
    

if __name__ == '__main__':
    # how many climbs to provide recommendations for
    BEST = int(1e1)
    LIMIT = int(1e2)
    
    # test data contains only colorado and utah
    climb = pd.read_csv('../scraping/all_data/climb.csv', index_col=0)
    
    # sort by starvotes descending
    climb = climb.sort_values('starvotes', ascending=False)
    
    FIT = meas.create_recommendation_system(climb[:LIMIT])
    
    # connect to db
    conn = sqlite3.connect(DB)
    print conn
    #with open('schema.sql', 'r') as f:
    #    conn.cursor().executescript(f.read())
    # keeps the database from complaining
    conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")

    counter = 0
    for href in climb.index[:BEST]:
        print str(counter) + " | " + str(href)
        counter += 1
        
        insert_recco(conn, href, climb, FIT)
        conn.commit()
    
    conn.close()