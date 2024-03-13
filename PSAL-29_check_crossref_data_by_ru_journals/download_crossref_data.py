import os
import time
import json
import pandas as pd
from habanero import Crossref
from requests.exceptions import HTTPError

data_folder = os.path.join(os.path.dirname(__file__), '../../data/ANALYTICS-115')
crossref = Crossref()
df = pd.read_csv(f"{data_folder}/log_openalex_download.csv").query('works_count > 0')
doi_df = pd.DataFrame(columns=['openalex_id', 'doi'])

# Формируем список DOI для работы
for i, r in df.iterrows():
    works_path, openalex_id = r['works_path'], r['openalex_id']

    if os.path.isfile(works_path):
        with open(works_path, 'r') as f:
            json_data = json.load(f)

        doi_df = pd.concat([
            doi_df,
            pd.DataFrame({'openalex_id': openalex_id, 'doi': [x['doi'].replace('https://doi.org/', '') for x in json_data]})
        ], ignore_index=True)

doi_df['status'] = 'In progress'

# Собираем данные по DOI из Crossref
for i, r in doi_df.iterrows():
    doi = r['doi']
    doi_folder = f"{data_folder}/crossref/{'/'.join(doi.split('/')[:-1])}"
    doi_path = f"{data_folder}/crossref/{doi}.json"

    if i % 10 == 0:
        print(f"{i+1}/{len(doi_df.index)} in progress...", end='\r')

    if not os.path.isdir(doi_folder):
        os.makedirs(doi_folder)

    if not os.path.isfile(doi_path):
        try:
            crossref_resp = crossref.works(ids=doi)

            with open(doi_path, 'w') as f:
                json.dump(crossref_resp, f, indent=4, ensure_ascii=False)
        except HTTPError as e:
            if e.response.status_code == 404:
                print(f"{doi} id skipped...")
            else:
                raise Exception(e)

        time.sleep(0.5)

    doi_df.loc[i, 'status'] = 'Done'

doi_df.to_csv(f"{data_folder}/log_crossref_download.csv", index=False)
