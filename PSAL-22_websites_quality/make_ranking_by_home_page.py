import os
import json
import pandas as pd

data_folder = '../data/PSAL-22'
universities = pd.read_excel(f"{data_folder}/universities_with_home_pages_final.xlsx")
universities_count = len(universities)
devices_types = ['desktop', 'mobile']
ranking_categories = ['performance', 'accessibility', 'best-practices', 'seo']
ranking = universities[['title_display', 'domain', 'home_page']].rename(columns={'title_display': 'university'})

for i, u in ranking.iterrows():
    domain = u['domain']
    file_path_prefix = f"{'0' * (len(str(universities_count)) - len(str(i))) + str(i)}_{domain.replace('.', '_')}"

    for dt in devices_types:
        json_data = None

        for folder_result in ['api', 'cli']:
            file_path = f"{data_folder}/home_page_check_results/{folder_result}/{file_path_prefix}_{dt}.json"

            if os.path.isfile(file_path):
                json_data = json.load(open(file_path, 'r')) if folder_result == 'cli' else json.load(open(file_path, 'r'))['lighthouseResult']

        if json_data:
            for rc in ranking_categories:
                ranking.loc[i, f"{dt}_{rc.replace('-', '_')}"] = json_data['categories'][rc]['score']

ranking = ranking.fillna(0)
ranking['rank'] = ranking[ranking.columns[3:]].sum(axis=1)
ranking = ranking.sort_values(by='rank', ascending=False).reset_index(drop=True)

#%% Сохраняем результаты

ranking.to_csv(f"{data_folder}/ranking.csv", index=False)
ranking.to_excel(f"{data_folder}/ranking.xlsx", index=False)

ranking_for_blog = ranking[~ranking['university'].isin(['МГППУ', 'ОГУ'])].copy()
ranking_for_blog['link'] = ranking_for_blog.apply(lambda x: f'<a href="{x["home_page"]}">{x["university"]}</a>', axis=1)
ranking_for_blog[['link', 'domain', 'rank']].to_html(f"{data_folder}/ranking.html")
