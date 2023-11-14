import os
import pandas as pd
import numpy as np

from tqdm import tqdm

import multiprocessing
from p_tqdm import p_map
   

def drop_start(config):
    df_origin = pd.read_csv(config['path'], low_memory = False)
    df_origin['category_small'] = df_origin.apply(lambda x : x['bigPath'] + '//' + x['middlePath'] + '//' + x['smallPath'], axis = 1)

    condition = df_origin.groupby(['New IP'])['URL'].count().reset_index().query('URL > 1')['New IP']

    if os.path.isfile(config['output_path']):
        os.remove(config['output_path'])

    df_origin.loc[~df_origin['New IP'].isin(condition)].to_csv(config['output_path'],
                                                               encoding = 'utf-8-sig',
                                                               index = False)
    
    df_origin = df_origin.loc[df_origin['New IP'].isin(condition)]
    groups = df_origin.groupby(['New IP'])

    with multiprocessing.Pool(multiprocessing.cpu_count() - 2) as pool:
        list(tqdm(pool.imap(drop_duplicates, [group for name, group in groups]), total = len(groups)))
  


def drop_duplicates(x):
    value = x.loc[:,'category_small']
    value.index = range(len(value))
    value_copy = value.iloc[1:]

    value_copy = pd.DataFrame({'old' : value_copy})
    value = pd.DataFrame({'new' : value})

    value_copy = pd.concat([value_copy, pd.DataFrame({'old' : ['end']})], axis = 0)
    value_copy.index = range(len(value_copy))

    concat = pd.concat([value, value_copy], axis = 1, ignore_index = True)
    concat.columns = ['new', 'old']

    index = concat.loc[concat.apply(lambda x : x['new'] != x['old'], axis = 1)].index
    result = x.iloc[index]
    
    result.to_csv('../Data/Preprocessed/drop_category.csv',
                  encoding = 'utf-8-sig',
                  index = False,
                  mode = 'a')


if __name__ == '__main__':
    config = {'path' : '../Data/Preprocessed/innerOutTaged.csv',
              'output_path' : '../Data/Preprocessed/drop_category.csv'}
    
    drop_start(config)