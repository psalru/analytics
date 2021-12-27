import pandas as pd
import requests

university = pd.read_csv('data/university.csv')

for i, row in university.iterrows():
    id = row['id']
    resp = requests.get('https://lk.priority2030.ru/api/v0/priority/' + id + '/info')

    if resp.status_code == 200:
        json = resp.text

        with open('data/university_data/' + str(i) + '.json', 'w') as file:
            file.write(json)
