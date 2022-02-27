from bs4 import BeautifulSoup
import pandas as pd
import re


def get_programs_data_by_university(index):
    path = 'data/pages/' + str(index) + '.html'

    with open(path) as f:
        content = f.read()

        soup = BeautifulSoup(content)
        semantic_data = soup.find_all(attrs={'itemprop': 'eduCode'})
        semantic_codes = {'ministry': set(), 'other': set()}

        reg = '\d\d\.\d\d\.\d\d[^\d]'
        regexp_data = re.findall(reg, content)
        regexp_codes = {'ministry': set(), 'other': set()}

        for code in regexp_data:
            code = code[:-1]

            if code in programs.index:
                regexp_codes['ministry'].add(code)
            else:
                regexp_codes['other'].add(code)

        for tag in semantic_data:
            codes_in_tag = re.findall(reg, tag.text)

            if len(codes_in_tag) > 0:
                code = codes_in_tag[0][:-1]

                if code in programs.index:
                    semantic_codes['ministry'].add(code)
                else:
                    semantic_codes['other'].add(code)

        return {
            'index': index,
            'semantic_ministry_count': len(semantic_codes['ministry']),
            'semantic_other_count': len(semantic_codes['other']),
            'semantic_count': len(semantic_codes['ministry']) + len(semantic_codes['other']),
            'semantic_ministry': semantic_codes['ministry'],
            'semantic_other': semantic_codes['other'],
            'regexp_ministry_count': len(regexp_codes['ministry']),
            'regexp_other_count': len(regexp_codes['other']),
            'regexp_count': len(regexp_codes['ministry']) + len(regexp_codes['other']),
            'regexp_ministry': regexp_codes['ministry'],
            'regexp_other': regexp_codes['other'],
        }


html = pd.read_csv('data/download_report.csv')
programs = pd.read_csv('data/all_education_programs.csv').set_index('program_number')

# Оставляем только университеты со скачанными данными
html = html[~html['isCandidate'] & (html['is_download'] | html['is_manually'])]
stats = pd.DataFrame(columns={
    'name': str,
    'url': str,
    'semantic_ministry_count': int,
    'semantic_other_count': int,
    'semantic_count': int,
    'semantic_ministry': set,
    'semantic_other': set,
    'regexp_ministry_count': int,
    'regexp_other_count': int,
    'regexp_count': int,
    'regexp_ministry': set,
    'regexp_other': set,
})

count = 0

for i, row in html.iterrows():
    name = row['name']
    programs_data = get_programs_data_by_university(row['id'])

    stats.loc[i] = {
        'name': name,
        'url': row['site'] + row['path'],
        'semantic_ministry_count': programs_data['semantic_ministry_count'],
        'semantic_other_count': programs_data['semantic_other_count'],
        'semantic_count': programs_data['semantic_count'],
        'semantic_ministry': programs_data['semantic_ministry'],
        'semantic_other': programs_data['semantic_other'],
        'regexp_ministry_count': programs_data['regexp_ministry_count'],
        'regexp_other_count': programs_data['regexp_other_count'],
        'regexp_count': programs_data['regexp_count'],
        'regexp_ministry': programs_data['regexp_ministry'],
        'regexp_other': programs_data['regexp_other'],
    }

    if count > 30:
        break

    count += 1

# html = pd.read_csv('data/pages_and_names.csv')
# programs = pd.read_csv('data/all_education_programs.csv').set_index('program_number')
# result = pd.DataFrame()
#
# for index, row in html[html['path'].notnull()].itterows():
#     get_programs(index)
#
#     break
