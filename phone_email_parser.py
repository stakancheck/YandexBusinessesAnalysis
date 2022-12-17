import re
import requests
from pprint import pprint


DEBUG_MODE = False


class PhoneEmailScraper:
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

    def __call__(self, html_content: str) -> dict[str, list[str]]:
        return {
            'emails': PhoneEmailScraper.get_emails(html_content),
            'phones': PhoneEmailScraper.get_phones(html_content)
        }

    @staticmethod
    def get_emails(html_content: str) -> list[str]:
        email = re.findall('[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,5}', html_content)
        email = list(set(email))

        return email if email else []

    @staticmethod
    def phone_validate(number: str) -> bool:
        data = {
            'tel': number[-10:],
        }
        response = requests.post('https://spys.one/tel/', headers=PhoneEmailScraper.headers, data=data)

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
    def get_phones(html_content: str) -> list[str]:
        phone = re.findall(r"[^a-zA-Z0-9]\+?[78]\s?[\s(]?[0-9]{3}[\-)]?\s?[0-9]"
                           r"{3}[-\s]?\s?[0-9]{2}[-,\s]?\s?[0-9]{2}[^a-zA-Z0-9]", html_content)
        phone = list(set(map(PhoneEmailScraper.phone_formatter, phone)))

        # Validate phone with spys.one (Only 50 requests per hour)
        if PhoneEmailScraper.validate_phones:
            phone = list(filter(PhoneEmailScraper.phone_validate, phone))

        results: list[str] = phone

        if PhoneEmailScraper.parse_town_phones:
            town_phone = re.findall(r'[^a-zA-Z0-9/][0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}[^a-zA-Z0-9/]', html_content)
            town_phone = list(set(map(PhoneEmailScraper.phone_formatter, town_phone)))
            results: list[str] = phone + town_phone

        results = list(filter(lambda x: x != '+79999999999', results))

        return results if results else []


if __name__ == '__main__':
    with open('downloader/site_dir_avtotsentr-kgs-ulitsa-60-let-oktjabrja.clients.site/save.html', 'r') as file:
        content = file.read()
        parser = PhoneEmailScraper()
        if DEBUG_MODE:
            pprint(parser(content))

