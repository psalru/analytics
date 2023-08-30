import re
import socket
import urllib3
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from helpers.psal_api import get_data_by_url

urllib3.disable_warnings()

session = requests.session()
session.headers.update({
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
})

#%% Исходный список университетов

ulist = get_data_by_url('https://app.psal.ru/api/university/')
udf = pd.json_normalize(ulist)[['id', 'title_short', 'title_display', 'domain']]

#%% Проверка истории с www


def www_check(s: pd.Series) -> pd.Series:
    domain = s['domain']

    try:
        ip_address = socket.gethostbyname(domain)
    except socket.gaierror:
        ip_address = np.NaN

    try:
        ip_address_www = socket.gethostbyname('www.' + domain)
    except socket.gaierror:
        ip_address_www = np.NaN

    # www_check_result = ip_address == ip_address_www if ip_address != np.NaN or ip_address_www != np.NaN else False

    return pd.concat([s, pd.Series({
        '@': ip_address,
        'www': ip_address_www,
        # 'www_check': www_check_result
    })])


udf_stage_01 = udf.apply(www_check, axis=1)

#%% Проверяем различные точки входа


def get_final_url(url: str, redirect_count=0):
    try:
        resp_head = session.head(url, timeout=5)
    except requests.exceptions.SSLError:
        resp_head = session.head(url, verify=False, timeout=5)
    except requests.exceptions.ConnectTimeout:
        return np.NaN
    except requests.exceptions.ConnectionError:
        return np.NaN

    redirect_target = None

    if resp_head.status_code == 200:
        # Костыль из-за спорного решения на https://ulsu.ru/
        try:
            resp_get = session.get(url, verify=False, timeout=5)
        except requests.exceptions.ReadTimeout:
            return np.NaN
        except requests.exceptions.ConnectionError:
            return np.NaN

        soup = BeautifulSoup(resp_get.text)
        meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})

        if meta_refresh and len(meta_refresh.attrs['content'].split(';')) > 1:
            redirect_target = re.sub(r'url=', '', meta_refresh.attrs['content'].split(';')[1], flags=re.IGNORECASE)
        else:
            return url
    elif str(resp_head.status_code)[:2] == '30':
        redirect_target = resp_head.headers['Location']

    if redirect_count > 5:
        return np.NaN

    # Обрабатываем редиректы
    if redirect_target:
        redirect_url = redirect_target

        if not re.match(r'http[s]?:\/\/', redirect_target):
            location = '/' + redirect_target if redirect_target[:1] != '/' else redirect_target
            redirect_url_prefix = re.match(r'http[s]?:\/\/[\w\d\.]+', url).group()
            redirect_url = redirect_url_prefix + location

        return get_final_url(redirect_url, redirect_count + 1)

    return np.NaN


udf_stage_02 = udf_stage_01.copy()

for i, r in udf_stage_02.iterrows():
    domain = r['domain']

    print(f"{i} / {len(udf_stage_02) - 1} - {r['title_display']}", end='\r')

    for protocol in ['https', 'http']:
        for subdomain in ['@', 'www']:
            col_name = f"{protocol}_{subdomain}"
            url_home = f"{protocol}://{'' if subdomain == '@' else subdomain + '.'}{domain}/"
            udf_stage_02.loc[i, col_name] = get_final_url(url_home)


#%% Проверяем единство входа и определяем стартовую страницу


def set_data_by_home_page(s: pd.Series) -> pd.Series:
    home_page_variants = s[['https_@', 'https_www', 'http_@', 'http_www']].T
    home_page_ranking = home_page_variants.value_counts()
    data_by_home_page = pd.Series({'home_page': np.NaN, 'is_uniqueness': False, 'is_https': False})

    if len(home_page_ranking) > 0:
        home_page = home_page_ranking.dropna().index[0]

        data_by_home_page = pd.Series({
            'home_page': home_page,
            'is_uniqueness': len(home_page_variants.value_counts(dropna=False)) == 1,
            'is_https': home_page[:8] == 'https://'
        })

    return pd.concat([s, data_by_home_page])


udf_stage_03 = udf_stage_02.copy()
udf_stage_03 = udf_stage_03.apply(set_data_by_home_page, axis=1)

#%% Сохраняем результаты

udf_stage_03.to_csv('../data/PSAL-22/universities_with_home_pages.csv', index=False)
udf_stage_03.replace({False: 0, True: 1}).to_excel('../data/PSAL-22/universities_with_home_pages.xlsx', index=False)
