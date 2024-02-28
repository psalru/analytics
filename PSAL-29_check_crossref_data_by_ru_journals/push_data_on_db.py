import os
import json
import numpy as np
import pandas as pd
from helpers.s3 import s3, S3_BUCKET
from helpers.sql import get_engine

data_folder, s3_key_prefix = '../data/PSAL-29', 'datasets/tasks/PSAL-29'
journals = pd.read_csv(f"{data_folder}/russian_journals.csv").rename(columns={'title': 'journal'}).dropna(subset=['openalex'])
result = pd.DataFrame(columns=list(journals.columns[:6]) + ['doi', 'title', 'oa_author_count', 'oa_author_count_with_affiliations', 'cr_author_count', 'cr_author_count_with_affiliations', 'quality'])

for i, j in journals.iterrows():
    openalex_journal_id = j['openalex'].split('/')[-1]
    works_path = f"{data_folder}/works/{openalex_journal_id}.json"

    if os.path.isfile(works_path):
        works = json.load(open(works_path, 'r'))

        print(f"{i+1} of {len(journals)} in progress...", end='\r')

        for work in works:
            doi = work['doi'].replace('https://doi.org/', '')
            doi_path = f"{data_folder}/crossref/{doi}.json"

            if os.path.isfile(doi_path):
                crossref = json.load(open(doi_path, 'r'))
                cr_author_count = len(crossref['message']['author']) if 'author' in crossref['message'] else 0
                cr_author_count_with_affiliations = len(list(filter(lambda x: len(x['affiliation']) > 0, crossref['message']['author']))) if cr_author_count > 0 else 0

                result.loc[len(result)] = pd.concat([
                    pd.Series(j[journals.columns[:6]]),
                    pd.Series({
                        'doi': doi,
                        'title': work['display_name'] if 'display_name' in work.keys() and work['display_name'] else np.NaN,
                        'oa_author_count': len(work['authorships']),
                        'oa_author_count_with_affiliations': len(list(filter(lambda x: len(x['raw_affiliation_strings']) > 0, work['authorships']))),
                        'cr_author_count': cr_author_count,
                        'cr_author_count_with_affiliations': cr_author_count_with_affiliations,
                        'quality': cr_author_count_with_affiliations / cr_author_count if cr_author_count > 0 else 0
                    })
                ])
                s3.put_object(Body=bytes(json.dumps(work, indent=4, ensure_ascii=False), 'utf-8'), Key=f"{s3_key_prefix}/doi/{doi}/openalex.json", Bucket=S3_BUCKET)
                s3.put_object(Body=bytes(json.dumps(crossref, indent=4, ensure_ascii=False), 'utf-8'), Key=f"{s3_key_prefix}/doi/{doi}/crossref.json", Bucket=S3_BUCKET)

#%% Пушим результата в БД
engine = get_engine()
result.to_csv(f"{data_folder}/check_results.csv", index=False)
result.to_sql('psal_29_check_crossref_data_by_ru_journals', engine, if_exists='replace', index=False)
