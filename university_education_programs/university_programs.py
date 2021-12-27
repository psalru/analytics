from bs4 import BeautifulSoup
import pandas as pd
import re


def get_programs(index):
    path = 'data/pages/' + str(index) + '.html'
    result = pd.DataFrame()

    with open(path) as f:
        content = f.read()
        soup = BeautifulSoup(content)
        count_by_semantic = len(soup.find_all(attrs={'itemprop': 'eduCode'}))
        count_by_regexp = len(re.findall('\d\d\.\d\d\.\d\d[^\d]', content))

        print(index, count_by_semantic, count_by_regexp)


html = pd.read_csv('data/pages_and_names.csv')
programs = pd.read_csv('data/all_education_programs.csv').set_index('program_number')
result = pd.DataFrame()

for index, row in html[html['path'].notnull()].itterows():
    get_programs(index)
