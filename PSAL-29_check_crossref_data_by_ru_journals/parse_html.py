import os
import pandas as pd
from bs4 import BeautifulSoup

data_folder = '../../data/ANALYTICS-115'
data_folder_ni = '../../data/ANALYTICS-58'
ni = pd.read_excel(f"{data_folder_ni}/ni_2023_with_issn_from_oa_hm.xlsx")
df = pd.DataFrame(columns=['id', 'level', 'title', 'issn', 'doi_registrator', 'openalex', 'country', 'is_ru', 'is_ni', 'path'])
files = os.listdir(f"{data_folder}/html")
ni_issns = set()

# Добавляем ISSN-ы из Nature Index
for i, r in ni.iterrows():
    col_with_issn = 'oa_issn' if not pd.isnull(r['oa_issn']) else 'issn'

    for issn in r[col_with_issn].split(', '):
        ni_issns.add(issn)

for i, f in enumerate(files):
    if i % 500 == 0:
        print(f"{i}/{len(files)} in progress...", end='\r')

    journal_id, title, issn, doi_registrator, openalex, countries, level = int(f.split('.')[0]), '', [], '', [], [], 0
    path = os.path.join(data_folder, 'html', f)

    if os.path.isfile(path):
        html = open(path, 'r').read()
        soup = BeautifulSoup(html)
        block_tags = soup.select('.tab-content .col-lg-9 .row > *')
        header_tags = soup.select('.record-source-header > *')
        openalex_api_tags = soup.find_all('a', {'title': 'OpenAlex API'})
        level_tag = soup.select_one('.level-value')

        if len(header_tags) > 0:
            title = header_tags[0].text.strip()
            issn = [x.text.strip() for x in header_tags[1].find_all('a', {'title': 'ISSN Portal'})]

        if level_tag:
            level = int(level_tag.contents[0].text.strip())

        if openalex_api_tags and len(openalex_api_tags) > 0:
            openalex = [x.attrs['href'] for x in openalex_api_tags]

        for bt in block_tags:
            label_tag = bt.select_one('.details-label')
            label = label_tag.text.strip()

            if label == 'Агентство регистрации DOI':
                doi_registrator_tag = bt.select_one('.details-data')
                doi_registrator = doi_registrator_tag.text.strip()

            if label == 'Страна':
                country_tags = bt.select('.details-data .list-unstyled > li')
                countries = [str(x.contents[0]).strip() for x in country_tags] if len(country_tags) > 0 else countries

        df.loc[len(df)] = {
            'id': journal_id,
            'level': level,
            'title': title,
            'issn': ', '.join(issn),
            'doi_registrator': doi_registrator,
            'openalex': ', '.join(openalex),
            'country': ', '.join(countries),
            'is_ru': 'Россия' in countries,
            'is_ni': len(list(filter(lambda x: x in ni_issns, issn))) > 0,
            'path': path
        }

filtered_journals = df[((df['is_ru']) | (df['is_ni'])) & (df['doi_registrator'] == 'Crossref')].copy()
filtered_journals.to_csv(f'{data_folder}/filtered_journals.csv', index=False)
