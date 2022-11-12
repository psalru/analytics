import os
import ast
import pandas as pd

university_list = pd.read_csv('data/university_list.csv')
oecd_groups = pd.read_csv('data/oecd_goups.csv', dtype={'code': str}).set_index('code')
dump = pd.DataFrame()
objects = pd.DataFrame()
keywords = pd.DataFrame()
oecd = pd.DataFrame()
include_columns = {
    '_source.last_status.created_date': 'created_date',
    '_index': 'type',
    '_id': 'object_id',
    '_source.name': 'name',
}


for i, u in university_list[university_list['short_name'] != 'ВМА'].iterrows():
    rosrid_id = u['rosrid_id']
    folder_path = f'data/downloaded/{rosrid_id}'

    print(f'Work with {i+1} of {len(university_list)}')

    for object_type in ['nioktrs', 'rids', 'dissertations']:
        file_path = f'{folder_path}/{object_type}.csv'

        if os.path.isfile(file_path):
            df_object = pd.read_csv(file_path, index_col=0)

            if len(df_object) > 0:
                dump = pd.concat([dump, df_object])

                if object_type == 'dissertations':
                    df_object['_index'] = df_object['_source.dissertation_type.name'].apply(lambda x: 'doc_dissertations' if x == 'Докторская' else 'phd_dissertations')

                for j, o in df_object.iterrows():
                    object_id = o['_id']

                    keyword_list = ast.literal_eval(o['_source.keyword_list'])
                    df_keywords = pd.DataFrame(keyword_list)
                    df_keywords['object_id'] = object_id
                    keywords = pd.concat([keywords, df_keywords], ignore_index=True)

                    oecd_list = ast.literal_eval(o['_source.oecds'])
                    df_oecd = pd.DataFrame(oecd_list)
                    df_oecd['oecd_group'] = df_oecd['code'].apply(lambda x: oecd_groups.loc[x.split('.')[0]]['title'])
                    df_oecd['object_id'] = object_id
                    oecd = pd.concat([oecd, df_oecd], ignore_index=True)

                df_object = df_object[df_object.columns.difference(x for x in df_object.columns if x not in include_columns.keys())].rename(columns=include_columns)
                df_object['created_date'] = df_object['created_date'].apply(lambda x: x[0:10])
                df_object['rosrid_id'] = rosrid_id
                objects = pd.concat([objects, df_object], ignore_index=True)

#%%

university_list.to_csv('data/datalens/university.csv', index=False)
objects.to_csv('data/datalens/rosrid_objects.csv', index=False)
keywords.to_csv('data/datalens/rosrid_objects_keywords.csv', index=False)
oecd.to_csv('data/datalens/rosrid_objects_oecd.csv', index=False)

dump.to_excel('data/dump.xlsx', index=False)