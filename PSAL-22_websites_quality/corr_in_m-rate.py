import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

rank_site_url = 'https://xn----ftbfmepluu.xn--p1ai/api/universities/rating?type=site'
resp_rank = requests.get(rank_site_url)
df = pd.DataFrame()

if resp_rank.status_code == 200:
    json_data = resp_rank.json()
    df = pd.json_normalize(json_data['elements'])
    df['url'] = df['webname'].apply(lambda x: f"https://xn----ftbfmepluu.xn--p1ai/universities/{x}")

    for i, r in df.iterrows():
        url = r['url']
        resp = requests.get(r['url'])

        print(f"{i} / {len(df) - 1}: {r['shortName']}")

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text)

            for tag in soup.select('.univer-data .univer-data-item'):
                key = tag.find('div', {'class': 'univer-data-item__key'}).text.strip()
                value = tag.find('div', {'class': 'univer-data-item__value'}).text.strip()

                if key == 'Бюджетных мест:':
                    df.loc[i, 'students_count'] = int(value.replace(' ', ''))

        time.sleep(0.5)

#%% Смотрим корреляцию

data_folder = '../data/PSAL-22'
corr_matrix = df[~df['students_count'].isnull()][['points', 'students_count']].corr()
fig, ax = plt.subplots()
ax.scatter(x=df['points'], y=df['students_count'])
ax.set_xlabel('Количество очков полученных за сайт')
ax.set_ylabel('Количество бюджетных мест')
fig.suptitle(f"Коэффициент корреляции очков и бюджетных мест")
fig.set_figwidth(11)
fig.savefig(f"{data_folder}/m-rate_corr.png", format='png', bbox_inches='tight')
plt.close(fig)

df.to_csv(f"{data_folder}/m-rate_data.csv", index=False)
df.to_excel(f"{data_folder}/m-rate_data.xlsx", index=False)

