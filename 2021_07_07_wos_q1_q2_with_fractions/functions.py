import re


def get_magic_string(string: str):
    result: str = string
    result = result.lower()
    result = re.sub('[^a-zа-я]', '', result)

    return result


def get_affiliation_count(string: str, affiliation_list: list = []):
    separated_string = re.findall('\[[^\]]*\][^;]*', string)
    result = []

    for string_chunk in separated_string:
        affiliation_full: str = re.findall('[^]]*$', string_chunk)[0].strip()
        affiliation_name: str = re.findall('^[^,]*', affiliation_full)[0].strip()

        if len(affiliation_list) > 0:
            if get_magic_string(affiliation_name) in [get_magic_string(x) for x in affiliation_list]:
                affiliation_name = affiliation_list[0]

        result.append(affiliation_name)

    return len(set(result))


def get_my_affiliation_data(string: str, affiliation_list: list):
    separated = re.findall('\[[^\]]*\][^;]*', string)
    affiliation_string_without_my = ''
    result = {
        'packages': [],
        'count_affiliations_by_author': {},
    }

    for item in separated:
        authors_string: str = re.findall('\[[^\]]*\]', item)[0].replace('[', '').replace(']', '')
        affiliation_full: str = re.findall('[^]]*$', item)[0].strip()
        affiliation_name: str = re.findall('^[^,]*', affiliation_full)[0].strip()

        if get_magic_string(affiliation_name) in [get_magic_string(x) for x in affiliation_list]:
            author_list = authors_string.split('; ')

            result['packages'].append({
                'name': affiliation_name,
                'authors': author_list,
            })

            for author in author_list:
                if author not in result['count_affiliations_by_author'].keys():
                    result['count_affiliations_by_author'][author] = 1
        else:
            affiliation_string_without_my += item + '; '

    for author in result['count_affiliations_by_author']:
        regexp = '[^\[]*' + author + '[^\]]*'
        result['count_affiliations_by_author'][author] += len(re.findall(regexp, affiliation_string_without_my))

    return result


def get_faction(row):
    author_count = row['authors_count']
    one_faction = 1/author_count
    result = 0

    if len(row['my_affiliation']) > 0:
        for affiliation_count in row['my_affiliation']['count_affiliations_by_author'].values():
            result += one_faction / affiliation_count
    else:
        result = 0

    return result
