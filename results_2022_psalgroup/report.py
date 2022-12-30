import pandas as pd
import json

with open('data/data.json') as f:
    df = pd.json_normalize(json.load(f)['messages'])

df = df[df['from_id'].notnull()]
df['date'] = pd.to_datetime(df['date'])
df = df[df['date'].dt.year == 2022]
df['month'] = df['date'].dt.month

stat_author = df.groupby(by=['from_id'], as_index=False)[['from']].count()
stat_month = df.groupby(by=['month'], as_index=False)[['month']].count()

stat_author_with_name = stat_author.merge(df[['from_id', 'from']], how='left', left_on='from_id', right_on='from_id').drop_duplicates(subset=['from_id'])
stat_month.index += 1
stat_month.plot(kind='bar', title='Кол-во сообщений по месяцам', legend=False)
stat_author_with_name = stat_author_with_name[~stat_author_with_name['from_id'].isin(['channel1430086006', 'user1400175895'])]
stat_author_with_name.sort_values(by='from_x').tail(10).plot(kind='bar', x='from_y', y='from_x', legend=False,  title='TOP 10 авторов по кол-ву сообщений')