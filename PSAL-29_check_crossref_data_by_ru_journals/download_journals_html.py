import os
import time
import requests
import pandas as pd

data_folder = '../data/PSAL-29'
url_tmp = 'https://journalrank.rcsi.science/ru/record-sources/details/{0}/'
# Скачать исходный CSV-файл можно на странице https://journalrank.rcsi.science/ru/record-sources/
log = pd.DataFrame(columns=['journal_id', 'path'])
count_of_journals = 30040
session = requests.Session()

for journal_id in range(1, count_of_journals + 1):
    html_path = f"{data_folder}/html/{journal_id}.html"

    if not os.path.isfile(html_path):
        url = url_tmp.format(journal_id)
        resp = session.get(url)

        if resp.status_code == 200:
            with open(html_path, 'w') as f:
                f.write(resp.text)

            log.loc[len(log)] = {
                'journal_id': journal_id,
                'path': html_path
            }
        else:
            print(f"{url} return status code {resp.status_code}")

        time.sleep(0.1)
    else:
        log.loc[len(log)] = {
            'journal_id': journal_id,
            'path': html_path
        }

    print(f"{journal_id} / {count_of_journals} downloaded!", end='\r')

log.to_csv(f"{data_folder}/download_log.csv", index=False)
