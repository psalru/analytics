import requests
import pandas as pd

shools_resp = requests.post('https://api.socio.center/engineers/schools')
shools_df = pd.json_normalize(shools_resp.json()['data']['items'])
kpi_df = pd.DataFrame()

for i, r in shools_df.iterrows():
    slug = r['slug'].lower()
    url = f'https://api.socio.center/engineers/school/{slug}/indicators'
    kpi_resp = requests.get(url)
    kpi_json = kpi_resp.json()

    for group in kpi_json['data']:
        group_title = group['title']

        for item in group['items']:
            kpi_chunk = pd.DataFrame({
                'label': item['label'],
                'value': item['value']
            })
            kpi_chunk[['slug', 'group', 'indicator', 'unit', 'description', 'calculation_method']] = [
                slug,
                group_title,
                item['indicator'],
                item['unit'],
                item['description'],
                item['calculationMethod']
            ]

            kpi_df = pd.concat([kpi_df, kpi_chunk], ignore_index=True)

    print(f'{i+1}/{len(shools_df)} is done!', end='\r')

kpi_df = shools_df.merge(kpi_df, how='right', on='slug')

print('All KPI is download!')

#%% Сохраняем результаты

data_folder = '../data/PSAL-32'
kpi_df.to_excel(f'{data_folder}/kpi_data.xlsx', index=False)
