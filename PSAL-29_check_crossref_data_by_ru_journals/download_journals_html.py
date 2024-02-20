import os
import time
import requests
import pandas as pd

data_folder = '../data/PSAL-29'
url_tmp = 'https://journalrank.rcsi.science/ru/record-sources/details/{0}/'
# Скачать исходный CSV-файл можно на странице https://journalrank.rcsi.science/ru/record-sources/
df = pd.read_csv(f"{data_folder}/journalrank.csv", sep='\t', low_memory=False)
df_filtered = df[df['cref'] == 'Yes'][['title', 'level', 'oax_id', 'cref']].dropna(subset=['oax_id']).copy().reset_index(drop=True)
session = requests.Session()

for i, r in df_filtered.iterrows():
    journal_id, journal_title = i+1, r['title']
    html_path = f"{data_folder}/html/{journal_id}.html"

    if not os.path.isfile(html_path):
        url = url_tmp.format(journal_id)
        resp = session.get(url)

        if resp.status_code == 200:
            with open(html_path, 'w') as f:
                f.write(resp.text)

            df_filtered.loc[i, 'downloaded'] = html_path
        else:
            print(f"{url} return status code {resp.status_code}")

        time.sleep(0.1)
    else:
        df_filtered.loc[i, 'downloaded'] = html_path

    print(f"{journal_id} / {len(df_filtered)} - {journal_title} downloaded!", end='\r')

df_filtered.to_csv(f"{data_folder}/download_log.csv", index=False)
