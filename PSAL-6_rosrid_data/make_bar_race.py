import pandas as pd
import bar_chart_race as bcr

df = pd.read_excel('data/niokrs_2019-2023.xlsx')
df['date'] = df['date'].apply(lambda x: '.'.join(x.split('-')[:-1]))
pivot = pd.pivot_table(
    df,
    index='date',
    columns='university',
    values='id',
    aggfunc='count'
)
pivot.fillna(0, inplace=True)
pivot = pivot.cumsum()
pivot.drop(['2019.11', '2019.12'], inplace=True)
bcr.bar_chart_race(
    df=pivot,
    filename='data/niokrs_2019-2023.gif',
    sort='desc',
    n_bars=10,
    title='ТОП 10 по НИОКТР на промежутке 2020-2023 гг.',
    steps_per_period=25,
    period_length=1000,
    scale='linear',
    period_fmt='{x}'
)
