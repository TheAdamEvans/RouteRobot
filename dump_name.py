import pandas as pd

DATA_DUMP = './data/info.txt'

def read_info(fn):

    # read the entire file into a python array
    with open(fn, 'rb') as f:
        data = f.readlines()

    # remove the trailing "\n" from each line
    data = map(lambda x: x.rstrip(), data)

    # each element of 'data' is an individual JSON object.
    # have all the individual business JSON objects
    data_json_str = "[" + ','.join(data) + "]"

    # now, load it into pandas
    data_df = pd.read_json(data_json_str)
    
    return data_df

if __name__ == '__main__':
	d = read_info(DATA_DUMP)
	d = d.sample(frac=1)
	d['Name'].to_csv('./data/route_name.txt', encoding = 'utf8', index = False)