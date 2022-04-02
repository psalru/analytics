import pandas as pd
import requests

# начинаем со списка университетов
resp = requests.get('https://lk.priority2030.ru/api/v0/priority/list')

if resp.status_code == 200:
    json_university = resp.json()
    university = pd.json_normalize(json_university['data']['participants'])
    university['shortName'] = university.apply(lambda x: '{0} ({1})'.format(x['shortName'], x['city']), axis=1)

    # сохраняем в csv-шку
    university.to_csv('data/university.csv', index=False)




