import os
import json
import pandas as pd

data_folder = '../data/PSAL-21_rating_parsing'
universities = pd.read_excel(f"{data_folder}/universities_with_home_pages_final.xlsx")
universities_count = len(universities)
devices_types = ['desktop', 'mobile']
ranking_categories = ['performance', 'accessibility', 'best-practices', 'seo']
ranking = universities[['title_display', 'domain', 'home_page']].rename(columns={'title_display': 'university'})

for i, u in ranking.iterrows():
    domain = u['domain']
    file_path_prefix = f"{'0' * (len(str(universities_count)) - len(str(i))) + str(i)}_{domain.replace('.', '_')}"

    for dt in devices_types:
        file_path = f"{data_folder}/check_results/{file_path_prefix}_{dt}.json"

        if os.path.isfile(file_path):
            json_data = json.load(open(file_path, 'r'))

            for rc in ranking_categories:
                ranking.loc[i, f"{dt}_{rc.replace('-', '_')}"] = json_data['lighthouseResult']['categories'][rc]['score']

ranking = ranking.fillna(0)

#%% Строим рейтинг

for dt in devices_types:
    for rc in ranking_categories:
        col_name = f"{dt}_{rc.replace('-', '_')}"
        ranking[f"{col_name}_rank"] = ranking[col_name].rank(pct=True) * 100

ranking['rank'] = ranking[list(filter(lambda x: x[-5:] == '_rank', ranking.columns))].sum(axis=1)

#%% Сохраняем результаты

ranking.to_excel(f"{data_folder}/ranking.xlsx", index=False)
