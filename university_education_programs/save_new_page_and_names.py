import pandas as pd


def get_name_with_city(row):
    name = row['Название университета']

    if names_count.loc[name] > 1:
        city = row['Город']

        return name + ' (' + city + ')'

    return name


df = pd.read_csv('../combined_analytics_data/data/result.csv')
names_count = df['Название университета'].value_counts()
df['Название университета'] = df.apply(get_name_with_city, axis=1)
df['path'] = ''
df = df.rename(columns={
    'Название университета': 'name',
    'Сайт': 'site',
    'Кандидат': 'isCandidate'
})

result = df[['site', 'path', 'name', 'isCandidate']]
result.to_csv('data/pages_and_names.csv', index=False)
