from bs4 import BeautifulSoup as bs4
import multiprocessing.pool
from lxml import html
import os
import io
import re
import csv
import json
import requests
import pandas as pd
from tld import get_tld
from tqdm.asyncio import tqdm
from lxml import html

API_KEY = 'ad2573789ca9cb74054e1c1447032bdaf61c6ee4'
BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/'


def prov_inn_valid_10(target_inn):
    base = target_inn[:-1]
    factors_10 = [2, 4, 10, 3, 5, 9, 4, 6, 8, 0]
    sum_products = 0
    for digit in range(len(base)):
        sum_products += int(base[digit]) * factors_10[digit]
    result = sum_products % 11
    if result > 9:
        key = result % 10
    else:
        key = result
    if key == int(target_inn[-1]):
        return True
    else:
        return False


def prov_inn_valid_12(target_inn):
    base = target_inn[:-1]
    factors_12_1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0]
    factors_12_2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0]
    sum_products1 = 0
    for digit in range(len(base)):
        sum_products1 += int(base[digit]) * factors_12_1[digit]
    result1 = sum_products1 % 11
    if result1 > 9:
        key_1 = result1 % 10
    else:
        key_1 = result1
    sum_products2 = 0
    for digit in range(12):
        sum_products2 += int(target_inn[digit]) * factors_12_2[digit]
    result2 = sum_products2 % 11
    if result2 > 9:
        key_2 = result2 % 10
    else:
        key_2 = result2
    if key_1 == int(target_inn[10]) and key_2 == int(target_inn[11]):
        return True
    else:
        return False


def prov_ogrn_valid(target_ogrn):
    return int(target_ogrn[:12]) % 11 == int(target_ogrn[12])


def find_INN_OGRN(resource, query):
    url = BASE_URL + resource
    headers = {
        'Authorization': 'Token ' + API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'query': query
    }
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.json()


def get_INN(soup):
    INN_sp = []
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.lower().split())
    text = ' '.join(chunk for chunk in chunks if chunk)
    k = re.findall('(\d+)', text)
    for i in re.findall('(\d+)', text):
        if len(str(int(i))) == 10 and len(i) == 10:
            if len(find_INN_OGRN('party', i)['suggestions']) != 0:
                INN_sp.append(int(i))
        elif len(str(int(i))) == 12 and len(i) == 12:
            if len(find_INN_OGRN('party', i)['suggestions']) != 0:
                INN_sp.append(int(i))
        elif ((len(str(int(i))) == 11 and prov_inn_valid_10(str(int(i[:-1])))) or (
                len(str(int(i))) == 13 and prov_inn_valid_12(str(int(i[:-1]))))) and (
                i[-1] == '8' or i[-1] == '+' or i[-1] == ',' or i[-1] == '.' or i[-1] == '7'):
            if len(find_INN_OGRN('party', i[:-1])['suggestions']) != 0:
                INN_sp.append(int(i))
    return list(set(INN_sp))


def get_OGRN(soup):
    OGRN_sp = []
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.lower().split(" "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    for i in re.findall('(\d+)', text):
        if len(str(int(i))) == 13 and len(find_INN_OGRN('party', i)['suggestions']) != 0:
            OGRN_sp.append(int(i))
        elif len(str(int(i))) == 14 and prov_ogrn_valid(str(int(i[:-1]))) and (
                i[-1] == '8' or i[-1] == '+' or i[-1] == ',' or i[-1] == '.' or i[-1] == '7'):
            if len(find_INN_OGRN('party', i[:-1])['suggestions']) != 0:
                OGRN_sp.append(int(i))
    return list(set(OGRN_sp))


if __name__ == '__main__':
    for i in next(os.walk('downloader'))[1]:
        with open('downloader/{}/save.html'.format(i), 'r',
                  encoding="utf-8", errors='ignore') as file:
            content = file.read()
            soup = bs4(content, 'html.parser')
            data_of_site = {}
            for inn in get_INN(soup):
                data = find_INN_OGRN('party', inn)['suggestions']
                data_of_site['organization_name'] = find_INN_OGRN('party', inn)['suggestions'][0]['value']
                data_of_site['general_director'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['management'][
                    'name']
                data_of_site['type_of_company'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['type']
                data_of_site['registration_date'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['state'][
                    'registration_date']
                data_of_site['founders'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['founders']
                data_of_site['inn'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['inn']
                data_of_site['ogrn'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['ogrn']
                data_of_site['kpp'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['kpp']
                data_of_site['okpo'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['okpo']
                data_of_site['okato'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['okato']
                data_of_site['oktmo'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['oktmo']
                data_of_site['okogu'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['okogu']
                data_of_site['postal_code'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['address']['data'][
                    'postal_code']
                data_of_site['address'] = find_INN_OGRN('party', inn)['suggestions'][0]['data']['address']['value']
