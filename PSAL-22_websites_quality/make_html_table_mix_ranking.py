import pandas as pd

data_folder = '../data/PSAL-22'
df = pd.read_excel(f"{data_folder}/ranking_mix.xlsx")
df = df[df['country'] != 'Russia'][:50].reset_index(drop=True)
df['position'] = df.index + 1
df['link'] = df.apply(lambda x: f'<a href="{x["home_page"]}">{x["university"]}</a>', axis=1)
df.index = [x + 1 for x in df.index]
df[['link', 'country', 'score']].to_html(f"{data_folder}/ranking_mix.html")
