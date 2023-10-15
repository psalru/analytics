import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

data_folder, fig_width = '../data/PSAL-25', 13
texts = json.load(open('texts.json', 'r'))
data = pd.DataFrame(columns=['value'])
university = 'ИТМО'
data.loc['university', 'value'] = university
data.loc['datetime', 'value'] = datetime.now().strftime('%d.%m.%Y')
df = pd.read_csv('https://storage.yandexcloud.net/psal.public/hosts/psal/dumps/hh_university_vacancies_by_month.csv', sep='|', index_col=0)
df['salary'] = df.apply(lambda x: x['salary_to'] if not pd.isnull(x['salary_to']) else x['salary_from'], axis=1)
region = df[df['university_abbreviation'] == university][['region', 'id']].groupby(by='region', as_index=False).count().sort_values(by='id', ascending=False).iloc[0]['region']

#%% Про преподавателей

df_teachers = df[df['professional_roles'] == 'Учитель, преподаватель, педагог'].copy()
teachers_mean_by_rf = df_teachers['salary'].mean() / 1000
teachers_mean_by_region = df_teachers[df_teachers['region'] == region]['salary'].mean() / 1000
teachers_mean_by_university = df_teachers[df_teachers['university_abbreviation'] == university]['salary'].mean() / 1000
teachers_top_by_university = df_teachers[df_teachers['university_abbreviation'] == university].sort_values(by='salary', ascending=False).iloc[0]
stat_by_teachers = pd.DataFrame([
    {'title': 'РФ', 'value': teachers_mean_by_rf},
    {'title': region, 'value': teachers_mean_by_region},
    {'title': university, 'value': teachers_mean_by_university},
]).dropna()
data.loc['description_teachers', 'value'] = texts['empty'].format(
    prof_role='Учитель, преподаватель, педагог'
) if university not in list(stat_by_teachers['title'].unique()) else texts['not_empty'].format(
    prof_role='Учитель, преподаватель, педагог',
    percent_of_rf='{0:0.2%}'.format(teachers_mean_by_university / teachers_mean_by_rf),
    percent_of_region='{0:0.2%}'.format(teachers_mean_by_university / teachers_mean_by_region),
    top_salary=round(teachers_top_by_university['salary'] / 1000, 0),
    top_vacancy=teachers_top_by_university['title'],
    top_url=teachers_top_by_university['url']
)
fig, ax = plt.subplots()
ax.bar(stat_by_teachers['title'], stat_by_teachers['value'], color='green')
ax.set_ylim(0, stat_by_teachers['value'].max() * 1.15)

for i, r in stat_by_teachers.iterrows():
    ax.annotate(
        '{0:.2f} тыс. ₽'.format(r['value']),
        (r['title'], r['value']),
        va='bottom', ha='center', xytext=(0, 10),
        textcoords='offset points', fontweight='bold',
    )

fig.set_figwidth(fig_width)
fig.savefig(f"{data_folder}/stat_by_teachers.png", format='png', bbox_inches='tight')
plt.close(fig)

#%% Про исследователей

df_researcher = df[df['professional_roles'] == 'Научный специалист, исследователь'].copy()
stat_by_researcher = pd.DataFrame([
    {'title': 'РФ', 'value': df_researcher['salary'].mean() / 1000},
    {'title': region, 'value': df_researcher[df_researcher['region'] == region]['salary'].mean() / 1000},
    {'title': university, 'value': df_researcher[df_researcher['university_abbreviation'] == university]['salary'].mean() / 1000},
]).dropna()
researchers_mean_by_rf = df_researcher['salary'].mean() / 1000
researchers_mean_by_region = df_researcher[df_researcher['region'] == region]['salary'].mean() / 1000
researchers_mean_by_university = df_researcher[df_researcher['university_abbreviation'] == university]['salary'].mean() / 1000
researchers_top_by_university = df_researcher[df_researcher['university_abbreviation'] == university].sort_values(by='salary', ascending=False).iloc[0]
data.loc['description_researcher', 'value'] = texts['empty'].format(
    prof_role='Учитель, преподаватель, педагог'
) if university not in list(stat_by_researcher['title'].unique()) else texts['not_empty'].format(
    prof_role='Научный специалист, исследователь',
    percent_of_rf='{0:0.2%}'.format(researchers_mean_by_university / researchers_mean_by_rf),
    percent_of_region='{0:0.2%}'.format(researchers_mean_by_university / researchers_mean_by_region),
    top_salary=round(researchers_top_by_university['salary'] / 1000, 0),
    top_vacancy=researchers_top_by_university['title'],
    top_url=researchers_top_by_university['url']
)
fig, ax = plt.subplots()
ax.bar(stat_by_researcher['title'], stat_by_researcher['value'], color='orange')
ax.set_ylim(0, stat_by_researcher['value'].max() * 1.15)

for i, r in stat_by_researcher.iterrows():
    ax.annotate(
        '{0:.2f} тыс. ₽'.format(r['value']),
        (r['title'], r['value']),
        va='bottom', ha='center', xytext=(0, 10),
        textcoords='offset points', fontweight='bold',
    )

fig.set_figwidth(fig_width)
fig.savefig(f"{data_folder}/stat_by_researcher.png", format='png', bbox_inches='tight')
plt.close(fig)

#%% Распределение вакансий по проф. ролям

teachers_count = len(df_teachers[df_teachers['university_abbreviation'] == university])
researchers_count = len(df_researcher[df_researcher['university_abbreviation'] == university])
stat_by_professional_roles = pd.DataFrame([
    {
        'title': 'ППС',
        'value': teachers_count,
        'percent': teachers_count / len(df_teachers)
    },
    {
        'title': 'НР',
        'value': researchers_count,
        'percent': researchers_count / len(df_researcher)
    },
    {
        'title': 'Остальное',
        'value': len(df[df['university_abbreviation'] == university]) - teachers_count - researchers_count,
        'percent': (len(df[df['university_abbreviation'] == university]) - teachers_count - researchers_count) / len(df)
    },
])

fig, ax = plt.subplots()
ax.bar(stat_by_professional_roles['title'], stat_by_professional_roles['value'], color=['green', 'orange', 'gray'])
ax.set_ylim(0, stat_by_professional_roles['value'].max() * 1.15)

for i, r in stat_by_professional_roles.iterrows():
    ax.annotate(
        '{0:.0f} ({1:.2%}*)'.format(r['value'], r['percent']),
        (r['title'], r['value']),
        va='bottom', ha='center', xytext=(0, 10),
        textcoords='offset points', fontweight='bold',
    )

fig.set_figwidth(fig_width)
fig.savefig(f"{data_folder}/stat_by_professional_roles.png", format='png', bbox_inches='tight')
plt.close(fig)

#%% ТОП 10 вакансий по заработной плате

df_top_by_salary = df[~df['salary'].isnull()].sort_values(by='salary', ascending=False).reset_index()[:10]
annex_top_by_salary = df_top_by_salary[['title', 'salary', 'university_abbreviation', 'url']]
data.loc['top_vacancies', 'value'] = texts['top_by_salary'].format(
    regions='; '.join([f"{i} ({x['id']})" for i, x in df_top_by_salary[['region', 'id']].groupby(by='region').count().sort_values(by='id', ascending=False).iterrows()]),
    count=len(df_top_by_salary['professional_roles'].unique()),
    prof_roles='; '.join([f"{i} ({x['id']})" for i, x in df_top_by_salary[['professional_roles', 'id']].groupby(by='professional_roles').count().sort_values(by='id', ascending=False).iterrows()])
)
