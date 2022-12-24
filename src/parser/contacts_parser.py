import re
import requests

from pprint import pprint
from dataclasses import dataclass, field


DEBUG_MODE = False


@dataclass
class ContactsData:
    phone_numbers: list[str] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)


class ContactsParser:
    """
    Класс (инструмент) для парсинга и получения номеров телефонов и электронных почт с сайта
    """
    validate_phones = False
    parse_town_phones = False

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

    def __call__(self, html_content: str) -> ContactsData:
        """
        Псевдоним для get_ContactsParser.company_contacts()
        :param html_content: HTML код сайта
        :return: Объект ContactsData с номерами телефонов и электронными почтами компании
        """
        return ContactsParser.get_company_contacts(html_content=html_content)

    @staticmethod
    def get_company_contacts(html_content: str) -> ContactsData:
        """
        Функция для получения контактов с сайта
        :param html_content: HTML код сайта
        :return: Объект ContactsData с номерами телефонов и электронными почтами компании
        """

        contacts = ContactsData(
            phone_numbers=ContactsParser.get_phones(html_content),
            emails=ContactsParser.get_emails(html_content)
        )
        return contacts

    @staticmethod
    def email_filter(email: str) -> bool:
        res = True
        ignore_list = ['.svg', '.png', '.jpg', '.webp', '.bmp', '.gif', '.css', 'example', 'team@tilda.cc']
        for ignore in ignore_list:
            if ignore in email:
                res = False
        return res

    @staticmethod
    def get_emails(html_content: str) -> list[str]:
        email = re.findall('[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,5}', html_content)
        email = list(set(email))
        email = list(filter(ContactsParser.email_filter, email))

        return email if email else []

    @staticmethod
    def phone_validate(number: str) -> bool:
        data = {
            'tel': number[-10:],
        }
        response = requests.post('https://spys.one/tel/', headers=ContactsParser.headers, data=data)

        return not ('Некорректный номер телефона' in response.text or
                    'Номер не найден в базе или некорректный' in response.text)

    @staticmethod
    def phone_formatter(number: str) -> str:
        digits = ''.join(re.findall(r'\d+', number))
        if digits.startswith('8'):
            digits = '+7' + digits[1:]
        elif digits.startswith('7'):
            digits = '+' + digits
        return digits

    @staticmethod
    def phone_filter(number: str) -> bool:
        ignore_list = ['+79999999999', '+79997777777', '+79991112233', '+79998887777', '+79990000000']
        return not (number in ignore_list)

    @staticmethod
    def get_phones(html_content: str) -> list[str]:
        phone = re.findall(r"[^a-zA-Z0-9]\+?[78]\s?[\s(]?[0-9]{3}[\-)]?\s?[0-9]{3}[-\s]?\s?[0-9]{2}[-,\s]?\s?[0-9]{2}", html_content)
        phone2 = re.findall(r"[^a-zA-Z0-9]\+?[78]\s?[\s(]?[0-9]{4}[\-)]?\s?[0-9]{3}[-\s]?\s?[0-9]{3}", html_content)
        phone3 = re.findall(r"[^a-zA-Z0-9]\+?[78]\s?[\s(]?[0-9]{4}[\-)]?\s?[0-9]{2}[-\s]?\s?[0-9]{2}[-\s]?\s?[0-9]{2}", html_content)
        phone = list(set(map(ContactsParser.phone_formatter, phone + phone2 + phone3)))

        # Validate phone with spys.one (Only 50 requests per hour)
        if ContactsParser.validate_phones:
            phone = list(filter(ContactsParser.phone_validate, phone))

        results: list[str] = phone

        if ContactsParser.parse_town_phones:
            town_phone = re.findall(r'[^a-zA-Z0-9/][0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}[^a-zA-Z0-9/]', html_content)
            town_phone = list(set(map(ContactsParser.phone_formatter, town_phone)))
            results: list[str] = phone + town_phone

        results = list(filter(ContactsParser.phone_filter, results))

        return results if results else []


if __name__ == '__main__':
    with open('downloader/site_dir_avtotsentr-kgs-ulitsa-60-let-oktjabrja.clients.site/save.html', 'r') as file:
        content = file.read()
        parser = ContactsParser()
        if DEBUG_MODE:
            pprint(parser(content))

