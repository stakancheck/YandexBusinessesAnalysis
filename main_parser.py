import os
import logging
from pprint import pprint

import pandas as pd
from itertools import islice
from tqdm.asyncio import tqdm
from phone_email_parser import PhoneEmailScraper


DOWNLOAD_DIR = 'downloader'
FILE_NAME = 'save.html'
PROGRESS_BAR_ASCII = False
logging.basicConfig(level=logging.DEBUG, filename='logs.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


def get_phone_and_email(content: str) -> dict[str, list[str]]:
    scraper = PhoneEmailScraper()
    result = scraper(html_content=content)
    return result


if __name__ == '__main__':
    for path, sub_dirs, files in tqdm(islice(os.walk(DOWNLOAD_DIR), 1, None), ascii=PROGRESS_BAR_ASCII, desc='Main progress'):
        if FILE_NAME in files:
            site_name = path[len(DOWNLOAD_DIR) + len('/site_dir_'):]
            file_to_parse = path + '/' + files[0]

            logging.debug(f'Start scrapping site: {site_name}')

            with open(file_to_parse, 'rb') as file:
                html_content = str(file.read())

                # Get phones and emails
                phone_email_data = get_phone_and_email(content=html_content)
                logging.debug(f'Successfully get emails and phones for: {site_name}')

                # print(phone_email_data)

                file.close()
