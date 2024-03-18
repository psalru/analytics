import matplotlib.pyplot as plt
from helpers.sql import read_sql

data_folder = '../data/PSAL-29'
ru_df = read_sql('''select distinct on (id) id, journal_quality from psal_29_ru_journals order by id, journal_quality''', db='sandbox')
ni_df = read_sql('''select distinct on (id) id, journal_quality from psal_29_ni_journals order by id, journal_quality''', db='sandbox')

fig, ax = plt.subplots(1, 2, constrained_layout=True)
ax[0].hist(ru_df['journal_quality'], bins=5)
ax[0].set_title('Журналы из Российской Федерации')
ax[1].hist(ni_df['journal_quality'], bins=5)
ax[1].set_title('Журналы Nature Index')

fig.suptitle(f"Качество данных в журналах")
fig.set_figwidth(11)
fig.savefig(f"{data_folder}/ru_vs_ni_journals_hists.png", format='png', bbox_inches='tight')
plt.close(fig)
