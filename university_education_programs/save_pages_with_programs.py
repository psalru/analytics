import pandas as pd
import requests

df = pd.read_csv('data/pages_and_names.csv').fillna('')
df['is_download'] = False
df['is_manually'] = False

for i, row in df.iterrows():
    if row.path != '':
        url = row.site + row.path

        try:
            response = requests.get(url)

            if response.status_code == 200:
                    with open('data/pages/%d.html' % i, 'w') as file:
                        file.write(response.content.decode('utf-8'))
                    df.loc[i, 'is_download'] = True
                    print('good:', i, url)
        except BaseException:
            print('fail:', i, url)

df.to_csv('data/download_report.csv')
