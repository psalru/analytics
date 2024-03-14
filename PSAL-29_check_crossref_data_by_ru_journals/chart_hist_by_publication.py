import matplotlib.pyplot as plt
from helpers.sql import read_sql

data_folder = '../data/PSAL-29'
ru_df = read_sql('''select id, quality from psal_29_ru_journals''', db='sandbox')
ni_df = read_sql('''select id, quality from psal_29_ni_journals''', db='sandbox')

fig, ax = plt.subplots(1, 2, constrained_layout=True)
ax[0].hist(ru_df['quality'], bins=5)
ax[0].set_title('Публикации из журналов РФ')
ax[1].hist(ni_df['quality'], bins=5)
ax[1].set_title('Публикации из Nature Index')

fig.suptitle(f"Качество данных в публикациях")
fig.set_figwidth(11)
fig.savefig(f"{data_folder}/ru_vs_ni_publication_hists.png", format='png', bbox_inches='tight')
plt.close(fig)
