import sqlite3
import pandas as pd
import measure as meas
import re # booooo

def find_id(href):
    return re.search(r'(\d+)$',href).group(1)

def insert_recco(conn, href, climb, FIT, top=10):
    
    # get recommendation
    top_recco = meas.give_recommendation(FIT, href, top)

    # keep track of what route is being recommended
    o = {'origin_id': find_id(href)}
    origin = pd.DataFrame(o, index=top_recco.index)
    
    # subset the climb info and recco scores
    # must match schema.sql
    scores = top_recco[['combined_text','gradeComb','staraverage','best']]
    info = climb[['href_id','name','url','rateYDS','feet']]
    jnd = pd.concat([origin, info, scores], axis=1, join='inner')
    
    # replace float('NaN') with None to play nicely with sqlite3
    jnd = jnd.where((pd.notnull(jnd)), None)
    
    # run many insert statements
    jnd.to_sql('climb', conn, if_exists='append', index=False)
    

if __name__ == '__main__':
    # how many climbs to provide recommendations for
    BEST = 1000
    
    # test data contains only colorado and utah
    climb = pd.read_csv('_climb_test', index_col=0)
    climb['href_id'] = map(find_id, climb.index)
    climb['url'] = 'http://www.mountainproject.com/v/' + climb['href_id']
    # sort by starvotes descending
    climb = climb.sort_values('starvotes', ascending=False)
    
    FIT = meas.create_recommendation_system(climb)
    
    counter = 0
    for href in climb.index[:BEST]:
        print str(counter) + " | " + href
        counter += 1
        
        # connect to db
        conn = sqlite3.connect('climbon.db')
        # keeps the database from compaining
        conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        
        insert_recco(conn, href, climb, FIT)
        conn.commit()
        
        conn.close()