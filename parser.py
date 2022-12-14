import os
import re
import csv
import json

import requests
import pandas as pd
from tld import get_tld
from tqdm.asyncio import tqdm
from bs4 import BeautifulSoup as bs4

from lxml import html

import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Origin': 'https://spys.one',
    'Connection': 'keep-alive',
    'Referer': 'https://spys.one/tel/',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
}


def get_email(html):
    try:
        email = re.findall("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,5}",html)
        return email
    except:
        pass


def phone_validate(number: str) -> bool:
    data = {
        'tel': number[-10:],
    }
    response = requests.post('https://spys.one/tel/', headers=headers, data=data)

    return not ('Некорректный номер телефона' in response.text or
                'Номер не найден в базе или некорректный' in response.text)


def phone_formatter(number: str) -> str:
    res, n = re.subn(r'[-()\s]', '', number)
    return res


def get_phone(html: str) -> set[str]:
    try:
        phone = re.findall(r"\+?[78]\s?[\s(]?[0-9]{3}[\-)]?\s?[0-9]{3}[-\s]?\s?[0-9]{2}[-,\s]?\s?[0-9]{2}", html)
        phone = list(set(map(phone_formatter, phone)))
        phone = list(filter(phone_validate, phone))

        town_phone = re.findall(r'/[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}/', html)
        town_phone = list(set(map(phone_formatter, town_phone)))

        results = phone + town_phone

        return results

    except:
        pass


if __name__ == '__main__':
    with open('downloader/site_dir_chery-service-spb.ru/save.html', 'r') as file:
        content = file.read()
        soup = bs4(content, 'html.parser')
        print(get_email(soup.text))
        print(get_phone(soup.text))

