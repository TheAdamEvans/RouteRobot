import sqlite3
import pandas as pd
from shutil import copyfile

import measure as meas

DB = 'climbon.db'
SCHEMA = ['href','name','type','rateYDS','rateHueco','feet','keyword','img_src','img_height','img_width']


def insert_recco(conn, href, climb, FIT, top=20):
    
    # get recommendation
    top_recco = meas.give_recommendation(FIT, href, top)

    # keep track of what route is being recommended
    o = {'origin_href': href }
    origin = pd.DataFrame(o, index=top_recco.index)

    # subset the climb info and recco scores
    # must match schema.sql
    info = climb[SCHEMA]
    scores = top_recco['best']
    jnd = pd.concat([origin, info, scores], axis=1, join='inner')

    # replace float('NaN') with None to play nicely with sqlite3
    jnd = jnd.where((pd.notnull(jnd)), None)

    # run many insert statements
    jnd.to_sql('climb', conn, if_exists='append', index=False)
    conn.commit()
    

if __name__ == '__main__':
    # how many climbs to provide recommendations for
    BEST = int(1e3)
    
    # test data contains only colorado and utah
    print "Loading data..."
    climb = pd.read_pickle('../scraping/good_data/_climb')
    
    # sort by starvotes descending
    climb = climb.sort_values('starvotes', ascending=False)
    
    print "Creating recommendation system..."
    FIT = meas.create_recommendation_system(climb)
    
    # connect to db and reset climb table
    conn = sqlite3.connect(DB)
    with open('schema.sql', 'r') as f:
        conn.cursor().executescript(f.read())
        # keeps the database from complaining
        conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')

    # iterate through top routes and give recommendations
    counter = 0
    for href in climb.index[:BEST]:
        counter += 1
        print str(counter) + ' | ' + str(href)

        insert_recco(conn, href, climb, FIT)
    
    # print conn.cursor().execute("select * from climb order by best limit 100").fetchall()
    conn.close()

    print 'copying database to route-web folder...'
    copyfile('climbon.db', '../../route-web/climbon.db')
