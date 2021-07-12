#%%

import pandas as pd

j = pd.DataFrame()

for year in range(2018, 2021):
    for i in range(0, 7):
        df_journal_chunk = pd.json_normalize(pd.read_json('2021_07_07_wos_q1_q2_with_fractions/data/wos/{0}-{1}-{2}.json'.format(year, i*1000+1, i*1000+1000))['data'])
        j = pd.concat([j, df_journal_chunk])

j[['jcrYear', 'issn', 'eissn', 'quartile']].to_csv('2021_07_07_wos_q1_q2_with_fractions/data/wos-journals-q1-q2.csv', index=False)

#%%

