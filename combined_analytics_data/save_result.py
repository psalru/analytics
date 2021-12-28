import pandas as pd
import numpy as np
import json

university_list = pd.read_csv('data/university.csv').query('id != "4twacwymeq"')
university_names = university_list['shortName'].tolist()
result = pd.DataFrame(columns=university_names)

result.loc['Регион'] = university_list['region'].tolist()
result.loc['Субъект РФ'] = university_list['location'].tolist()
result.loc['Город'] = university_list['city'].tolist()
result.loc['Ведомство'] = university_list['founder'].tolist()
result.loc['Базовая часть'] = university_list['isBase'].tolist()
result.loc['Спец. часть'] = university_list['special'].tolist()
result.loc['Кандидат'] = university_list['isCandidate'].tolist()

for index, university in university_list.iterrows():
    with open('data/university_data/' + str(index) + '.json') as file:
        university_data = json.load(file)
        short_name = university_data['data']['shortName']

        # Данные ректора
        result.loc['Сайт', short_name] = university_data['data']['link']
        result.loc['Ректор', short_name] = university_data['data']['rectorName']

        # Участие в программах
        if 'programsList' in university_data['data'].keys():
            programs_list = pd.json_normalize(university_data['data']['programsList'])
            for i, row in programs_list.iterrows():
                result.loc[row['name'], short_name] = row['isParticipated']

        # Данные по секциям
        sections = pd.json_normalize(university_data['data']['sections'])

        for i, section in sections.iterrows():
            section_name = section['name']
            section_datas = pd.json_normalize(section['rows'])

            for j, section_data in section_datas.iterrows():
                section_data_models = pd.json_normalize(section_data['models'])

                for x, section_data_model in section_data_models.iterrows():
                    prop_title = section_data_model['props.title'] if 'props.title' in section_data_model.keys() else ''

                    if 'props.items' in section_data_model.keys():
                        section_data_model_items = pd.json_normalize(section_data_model['props.items'])
                        item_title = ''
                        item_value = np.NaN
                        make_record = False

                        for y, item in section_data_model_items.iterrows():
                            if 'value' in item.keys():
                                item_title = item['label']
                                item_value = float(item['value'])
                                make_record = True
                            elif 'text' in item.keys():
                                item_title = item['label']
                                item_text = item['text'].replace(' %', '').replace(' шт.', '').replace(',', '.')
                                item_value = float(item_text) if item_text != '' else 0
                                make_record = True
                            elif 'values' in item.keys():
                                item_title = item['label']
                                item_value = item['values'].pop()
                                make_record = True
                            # todo возможно как-то позже учтём тематические рейтинги
                            # else:
                            #     print(item)

                            if make_record:
                                result.loc[' / '.join([section_name, prop_title, item_title]).replace('/  /', '/'), short_name] = item_value

result = result.transpose()
result.to_csv('data/result.csv')
