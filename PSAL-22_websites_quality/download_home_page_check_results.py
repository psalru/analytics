import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_PAGESPEED')
data_folder = '../data/PSAL-22'
universities = pd.read_excel(f"{data_folder}/universities_with_home_pages_final.xlsx")
url_tpl = """
https://www.googleapis.com/pagespeedonline/v5/runPagespeed?key={api_key}
&category=ACCESSIBILITY
&category=BEST_PRACTICES
&category=PERFORMANCE
&category=PWA
&category=SEO
&strategy={strategy}
&url={url}
""".replace('\n', '')

for i, u in universities.iterrows():
    domain, home_page = u['domain'], u['home_page']

    print(f"{i} / {len(universities) - 1}: {home_page} in progress", end='\r')

    for strategy in ['DESKTOP', 'MOBILE']:
        number = f"{'0'*(len(str(len(universities) - 1)) - len(str(i))) + str(i)}"
        file_name = f"{number}_{domain.replace('.', '_')}_{strategy.lower()}.json"
        result_path = f"{data_folder}/home_page_check_results/api/{file_name}"

        if not os.path.isfile(result_path):
            resp = requests.get(url_tpl.format(
                api_key=api_key,
                strategy=strategy,
                url=home_page
            ))

            if resp.status_code == 200:
                json_data = resp.json()

                with open(result_path, 'w') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
            else:
                print(f"# {number} - for {home_page} ({strategy.lower()}) return status code {resp.status_code}")

print('All universities id checked!')
