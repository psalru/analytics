import re
import json
from helpers.sql import read_sql

data_folder = '../data/PSAL-29'
df = read_sql('''
select id, journal, openalex, level, avg(quality) as journal_quality from psal_29_check_crossref_data_by_ru_journals
group by id, journal, openalex, level order by id
''')
sql_add_2_columns = ''

for i, r in df.iterrows():
    openalex_id = r['openalex'].split('/')[-1]
    path = f"{data_folder}/openalex/{openalex_id}.json"
    json_data = json.load(open(path, 'r'))
    concept = json_data['x_concepts'][0]

    for c in json_data['x_concepts'][1:]:
        if c['level'] == 0 and c['score'] > concept['score']:
            concept = c

    df.loc[i, 'concept_title'] = concept['display_name']
    df.loc[i, 'concept_score'] = concept['score']
    sql_add_2_columns += f"""
    -- Журнал с id = {r['id']}
    update psal_29_check_crossref_data_by_ru_journals set
    journal_quality = {r['journal_quality']}, journal_concept = '{concept['display_name']}'
    where id = {r['id']};
    """

with open(f"{data_folder}/sql_add_2_new_columns.sql", 'w') as f:
    f.write(re.sub(r'^\s+', '', sql_add_2_columns, flags=re.MULTILINE))

df.to_excel(f"{data_folder}/stat_by_journals.xlsx", index=False)
