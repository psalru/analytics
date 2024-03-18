import os
import json
import math
import requests
import pandas as pd


def get_data_by_url(url: str, page=1, per_page=200, is_recursive=True) -> []:
    data = []
    query_url = f"{url}&page={page}&per-page={per_page}"
    resp = requests.get(query_url)

    if resp.status_code == 200:
        page_data = resp.json()
        total_count = page_data['meta']['count']
        page_count = math.ceil(total_count / per_page)
        data += page_data['results']

        print(f'{page} of {page_count}: {query_url}', end='\r')

        if is_recursive and page_count and page != page_count:
            data += get_data_by_url(works_url, page + 1)
    else:
        print(f'{query_url} return status code {resp.status_code}')

    return data


data_folder = '../data/PSAL-29'
df = pd.read_csv(f"{data_folder}/filtered_journals.csv").dropna(subset=['openalex'])
df['openalex'] = df['openalex'].apply(lambda x: x.split(', '))
df = df.explode('openalex').reset_index(drop=True)

# Находим ссылки на статьи журналов
for i, r in df.iterrows():
    journal_url, openalex_id = r['openalex'], r['openalex'].split('/')[-1]
    journal_path = f"{data_folder}/openalex/{openalex_id}.json"

    if not os.path.isfile(journal_path):
        print(f"{i+1} of {len(df)}: {journal_url} download...")

        resp_by_journal = requests.get(journal_url)

        if resp_by_journal.status_code == 200:
            json_data = resp_by_journal.json()

            with open(f"{data_folder}/openalex/{openalex_id}.json", 'w') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)

            df.loc[i, 'openalex_works_api_ulr'] = json_data['works_api_url']
        else:
            print(f"{journal_url} returned {resp_by_journal.status_code}")
    else:
        with open(journal_path, 'r') as f:
            json_data = json.load(f)
            df.loc[i, 'openalex_works_api_ulr'] = json_data['works_api_url']

log = pd.DataFrame(columns=['openalex_id', 'works_path', 'works_count'])

# Забираем данные из OpenAlex по статьям
for i, r in df.iterrows():
    openalex_id = r['openalex'].split('/')[-1]
    works_url = f"{r['openalex_works_api_ulr']},publication_year:2023"
    works_path = f"{data_folder}/works/{openalex_id}.json"

    if not os.path.isfile(works_path):
        print(f"{i+1} of {len(df)}: {works_url} download...")

        works = get_data_by_url(works_url)

        with open(works_path, 'w') as f:
            json.dump(works, f, indent=4, ensure_ascii=False)
    else:
        with open(works_path, 'r') as f:
            works = json.load(f)

    log.loc[len(log)] = {
        'openalex_id': openalex_id,
        'works_path': works_path,
        'works_count': len(works)
    }

log.to_csv(f"{data_folder}/log_openalex_download.csv", index=False)
