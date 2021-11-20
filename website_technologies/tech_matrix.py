import pandas as pd
import json


def read_tech(number):
    content = open(f'data/technologies/{number}.json', 'r').read()
    data = json.loads(content)
    site = pd.json_normalize(data, 'technologies')
    site['category'] = site['categories'].apply(lambda x: x[0]['name'])

    return site


university = pd.read_csv('data/sites_and_names.csv')
headers = ['Название', 'Категория'] + university['name'].to_list() + ['Количество']
result = pd.DataFrame(columns=headers)

for index, row in university.iterrows():
    university_name = row['name']
    university_site = row['site']
    technologies = read_tech(index)
    row = pd.Series([0] * len(university))

    for i, tech in technologies.iterrows():
        tech_name = tech['name']
        tech_category = tech['category']

        if tech_name not in result.index:
            result.loc[tech_name] = 0
            result.loc[tech_name, 'Название'] = tech_name
            result.loc[tech_name, 'Категория'] = tech_category
            result.loc[tech_name, university_name] += 1
            result.loc[tech_name, 'Количество'] += 1
        else:
            result.loc[tech_name, university_name] += 1
            result.loc[tech_name, 'Количество'] += 1

result = result.sort_values(by=['Категория', 'Количество'], ascending=[True, False]).reset_index(drop=True)
result.to_csv('data/resul.csv')

