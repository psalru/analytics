import time
import json
import requests
import pandas as pd
from pathlib import Path


def get_search_results(data, timeout=1):
    items_in_page = 10
    search_results = []

    try:
        resp = session.request("POST", search_url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))

        if resp.status_code == 200:
            json_resp = resp.json()
            page = data['page']
            total = json_resp['hits']['total']['value']
            count_of_pages = (int(total / items_in_page) + 1) if total % items_in_page else total / items_in_page

            print(f"Downloaded data from page {page} of {count_of_pages}")

            if page < count_of_pages:
                time.sleep(timeout)
                search_results += json_resp['hits']['hits'] + get_search_results({**data, 'page': page + 1}, timeout)
            else:
                search_results += json_resp['hits']['hits']
    except BaseException as e:
        print('Retry connection', str(e))
        search_results = get_search_results({**data, 'page': 1}, timeout)

    return search_results


university_list = pd.read_csv('data/university_list.csv')
search_url = 'https://rosrid.ru/api/base/search'

session = requests.session()
headers = json.loads(Path('headers.json').read_text())
session.headers.update(headers)
home_url = 'https://rosrid.ru/global-search'
home_resp = session.request('GET', home_url)
start_date = '2021-01-01'
end_date = '2022-11-01'
payload_tmpl = {**json.loads(Path('payload.json').read_text()), 'start_date': start_date, 'end_date': end_date}

if home_resp.status_code == 200:
    for i, university in university_list.iterrows():
        university_id = university['rosrid_id']
        university_folder = f'data/downloaded/{university_id}'

        print(f'Working with {university_id}: {i+1} of {len(university_list)}')

        if not Path(university_folder).is_dir():
            Path(university_folder).mkdir()

        for object_type in ['nioktrs', 'rids', 'dissertations']:
            df_path = f'{university_folder}/{object_type}.csv'

            if not Path(df_path).is_file():
                payload = {**payload_tmpl, 'organization': [university_id], f'{object_type}': True}
                df = pd.json_normalize(get_search_results(payload))
                df.to_csv(df_path)
            else:
                print(f'File {df_path} already exist!')

else:
    print(f'{home_url} return statis code {home_resp.status_code}')
