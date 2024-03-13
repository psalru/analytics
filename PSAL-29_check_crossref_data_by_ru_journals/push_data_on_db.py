import os
import json
import numpy as np
import pandas as pd
from helpers.s3 import s3, S3_BUCKET
from helpers.sql import get_engine


def get_concept_title(oa_id: str):
    if oa_id in concepts.index:
        return concepts.loc[oa_id, 'journal_concept']

    path = f"{data_folder}/openalex/{oa_id}.json"
    json_data = json.load(open(path, 'r'))
    concept = json_data['x_concepts'][0]

    if len(json_data['x_concepts']) == 0:
        return np.NaN

    for c in json_data['x_concepts'][1:]:
        if c['level'] == 0 and c['score'] > concept['score']:
            concept = c

    display_name = concept['display_name']
    concepts.loc[oa_id, 'journal_concept'] = display_name

    return display_name


data_folder, s3_key_prefix = '../data/PSAL-29', 'datasets/tasks/PSAL-29'
journals = pd.read_csv(f"{data_folder}/filtered_journals.csv").rename(columns={'title': 'journal'}).dropna(subset=['openalex'])
concepts = pd.DataFrame(columns=['journal_concept'])
result = pd.DataFrame(columns=list(journals.columns[:6]) + ['journal_index', 'journal_concept', 'doi', 'title', 'oa_author_count', 'oa_author_count_with_affiliations', 'cr_author_count', 'cr_author_count_with_affiliations', 'quality'])

for i, j in journals.iterrows():
    openalex_list = j['openalex'].split(', ')

    for openalex in openalex_list:
        openalex_journal_id = openalex.split('/')[-1]
        works_path = f"{data_folder}/works/{openalex_journal_id}.json"

        if os.path.isfile(works_path):
            works = json.load(open(works_path, 'r'))

            print(f"{i+1} of {len(journals)} in progress...", end='\r')

            for work in works:
                doi = work['doi'].replace('https://doi.org/', '')

                if doi not in result.index:
                    doi_path = f"{data_folder}/crossref/{doi}.json"

                    if os.path.isfile(doi_path):
                        crossref = json.load(open(doi_path, 'r'))
                        cr_author_count = len(crossref['message']['author']) if 'author' in crossref['message'] else 0
                        cr_author_count_with_affiliations = len(list(filter(lambda x: len(x['affiliation']) > 0, crossref['message']['author']))) if cr_author_count > 0 else 0

                        result.loc[doi] = pd.concat([
                            pd.Series(j[journals.columns[:6]]),
                            pd.Series({
                                'journal_index': 'ru' if j['is_ru'] else 'ni' if j['is_ni'] else np.NaN,
                                'doi': doi,
                                'title': work['display_name'] if 'display_name' in work.keys() and work['display_name'] else np.NaN,
                                'oa_author_count': len(work['authorships']),
                                'oa_author_count_with_affiliations': len(list(filter(lambda x: len(x['raw_affiliation_strings']) > 0, work['authorships']))),
                                'cr_author_count': cr_author_count,
                                'cr_author_count_with_affiliations': cr_author_count_with_affiliations,
                                'quality': cr_author_count_with_affiliations / cr_author_count if cr_author_count > 0 else 0,
                                'journal_concept': get_concept_title(openalex_journal_id),
                            })
                        ])
                        s3.put_object(Body=bytes(json.dumps(work, indent=4, ensure_ascii=False), 'utf-8'), Key=f"{s3_key_prefix}/doi/{doi}/openalex.json", Bucket=S3_BUCKET)
                        s3.put_object(Body=bytes(json.dumps(crossref, indent=4, ensure_ascii=False), 'utf-8'), Key=f"{s3_key_prefix}/doi/{doi}/crossref.json", Bucket=S3_BUCKET)

journals_quality = result[['id', 'quality']].groupby('id', as_index=False).mean().rename(columns={'quality': 'journal_quality'})
result = result.merge(journals_quality, how='left', on='id')

#%% Пушим результата в БД

engine = get_engine()
result.to_csv(f"{data_folder}/check_results.csv", index=False)
result[result['journal_index'] == 'ru'].to_sql('psal_29_ru_journals', engine, if_exists='replace', index=False)
result[result['journal_index'] == 'ni'].to_sql('psal_29_ni_journals', engine, if_exists='replace', index=False)
