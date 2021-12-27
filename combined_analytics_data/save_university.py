import pandas as pd
import requests

# начинаем со списка университетов
resp = requests.get('https://lk.priority2030.ru/api/v0/priority/list')

if resp.status_code == 200:
    json_university = resp.json()
    university = pd.json_normalize(json_university['data']['participants'])

    # сохраняем в csv-шку
    university.to_csv('data/university.csv', index=False)




