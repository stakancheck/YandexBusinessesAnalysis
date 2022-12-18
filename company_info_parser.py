import os
import re
import json
from itertools import islice

import requests

from pprint import pprint
from bs4 import BeautifulSoup as bs4
from dataclasses import dataclass, field


API_KEY = 'ad2573789ca9cb74054e1c1447032bdaf61c6ee4'
BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/'
DEBUG_MODE = False


@dataclass
class CompanyInfoData:
    organization_name: list[str] = field(default_factory=list)
    general_director: list[str] = field(default_factory=list)
    type_of_company: list[str] = field(default_factory=list)
    registration_date: list[str] = field(default_factory=list)
    founders: list[str] = field(default_factory=list)
    inn: list[str] = field(default_factory=list)
    ogrn: list[str] = field(default_factory=list)
    kpp: list[str] = field(default_factory=list)
    okpo: list[str] = field(default_factory=list)
    okato: list[str] = field(default_factory=list)
    oktmo: list[str] = field(default_factory=list)
    okogu: list[str] = field(default_factory=list)
    postal_code: list[str] = field(default_factory=list)
    address: list[str] = field(default_factory=list)


class CompanyInfoParser:
    """
    Класс (инструмент) для парсинга ИНН, ОГРН и других данных компании
    """
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def prov_ogrn_valid(target_ogrn):
        return int(target_ogrn[:12]) % 11 == int(target_ogrn[12])

    @staticmethod
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

    @staticmethod
    def get_INN(soup: bs4):
        INN_sp = []
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.lower().split())
        text = ' '.join(chunk for chunk in chunks if chunk)
        for digit in re.findall('(\d+)', text):
            if len(str(int(digit))) == 10 and len(digit) == 10:
                if len(CompanyInfoParser.find_INN_OGRN('party', digit)['suggestions']) != 0:
                    INN_sp.append(int(digit))
            elif len(str(int(digit))) == 12 and len(digit) == 12:
                if len(CompanyInfoParser.find_INN_OGRN('party', digit)['suggestions']) != 0:
                    INN_sp.append(int(digit))
            elif ((len(str(int(digit))) == 11 and CompanyInfoParser.prov_inn_valid_10(str(int(digit[:-1])))) or (
                    len(str(int(digit))) == 13 and CompanyInfoParser.prov_inn_valid_12(str(int(digit[:-1]))))) and (
                    digit[-1] == '8' or digit[-1] == '+' or digit[-1] == ',' or digit[-1] == '.' or digit[-1] == '7'):
                if len(CompanyInfoParser.find_INN_OGRN('party', digit[:-1])['suggestions']) != 0:
                    INN_sp.append(int(digit))
        return list(set(INN_sp))

    @staticmethod
    def get_OGRN(soup: bs4):
        OGRN_sp = []
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.lower().split(" "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        for digit in re.findall('(\d+)', text):
            if len(str(int(digit))) == 13 and len(CompanyInfoParser.find_INN_OGRN('party', digit)['suggestions']) != 0:
                OGRN_sp.append(int(digit))
            elif len(str(int(digit))) == 14 and CompanyInfoParser.prov_ogrn_valid(str(int(digit[:-1]))) and (
                    digit[-1] == '8' or digit[-1] == '+' or digit[-1] == ',' or digit[-1] == '.' or digit[-1] == '7'):
                if len(CompanyInfoParser.find_INN_OGRN('party', digit[:-1])['suggestions']) != 0:
                    OGRN_sp.append(int(digit))
        return list(set(OGRN_sp))

    @staticmethod
    def get_inn_data_from_html(html_content: str) -> CompanyInfoData:
        """
        Функция получения информации о компании с сайта
        :param html_content: HTML код сайта
        :return: Объект CompanyInfoData со всей информацией о компании
        """
        soup = bs4(html_content, 'html.parser')  # parse to bs4 soup
        info = CompanyInfoData()  # create default data

        for inn in CompanyInfoParser.get_INN(soup):
            # Get data
            data = CompanyInfoParser.find_INN_OGRN('party', inn)['suggestions'][0]

            if DEBUG_MODE:
                pprint(data)

            # Update dict and paste new data from found INN code
            info.organization_name.append(data['value'])
            if 'management' in data['data']:
                info.general_director.append(data['data']['management']['name'])
            else:
                info.general_director.append(data['data']['name']['full'])
            info.type_of_company.append(data['data']['type'])
            info.registration_date.append(data['data']['state']['registration_date'])
            if 'founders' in data['data']:
                info.founders.append(data['data']['founders'])
            if 'inn' in data['data']:
                info.inn.append(data['data']['inn'])
            if 'ogrn' in data['data']:
                info.ogrn.append(data['data']['ogrn'])
            if 'kpp' in data['data']:
                info.kpp.append(data['data']['kpp'])
            if 'okpo' in data['data']:
                info.okpo.append(data['data']['okpo'])
            if 'okato' in data['data']:
                info.okato.append(data['data']['okato'])
            if 'oktmo' in data['data']:
                info.oktmo.append(data['data']['oktmo'])
            if 'okogu' in data['data']:
                info.okogu.append(data['data']['okogu'])
            if 'address' in data['data']:
                info.postal_code.append(data['data']['address']['data']['postal_code'])
                info.address.append(data['data']['address']['value'])

        return info

    def __call__(self, html_content: str) -> CompanyInfoData:
        """
        Псевдоним для CompanyInfoParser.get_inn_data_from_html()
        :param html_content: HTML код сайта
        :return: Объект CompanyInfoData со всей информацией о компании
        """
        return CompanyInfoParser.get_inn_data_from_html(html_content=html_content)


if __name__ == '__main__':
    # Parse all files from downloader dir

    for path, sub_dirs, files in islice(os.walk('downloader'), 1, None):
        if 'save.html' in files:
            file_to_parse = path + '/' + files[0]
            with open(file_to_parse, 'rb') as file:
                content = str(file.read())

                info_parser = CompanyInfoParser()
                info_parser(html_content=content)
                # pprint(info_parser(html_content=content))
