import pandas as pd

actives = pd.read_csv('data/datalens/rosrid_objects.csv', date_parser=['created_date'])
actives['name_len'] = actives['name'].apply(lambda x: len(x))
print(actives['name_len'].max())
