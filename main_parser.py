import os
import logging
import pandas as pd
from pprint import pprint
from itertools import islice
from tqdm.asyncio import tqdm
from contacts_parser import ContactsParser, ContactsData
from company_info_parser import CompanyInfoParser, CompanyInfoData


DOWNLOAD_DIR = 'downloader'
FILE_NAME = 'save.html'
PROGRESS_BAR_ASCII = False
logging.basicConfig(level=logging.DEBUG, filename='logs.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


def get_phone_and_email(content: str) -> ContactsData:
    scraper = ContactsParser()
    result = scraper.get_company_contacts(html_content=content)
    return result


def get_company_info(content: str) -> CompanyInfoData:
    scraper = CompanyInfoParser()
    result = scraper.get_inn_data_from_html(html_content=content)
    return result


if __name__ == '__main__':
    for path, sub_dirs, files in tqdm(islice(os.walk(DOWNLOAD_DIR), 1, None),
                                      ascii=PROGRESS_BAR_ASCII, desc='Main progress'):
        if FILE_NAME in files:
            site_name = path[len(DOWNLOAD_DIR) + len('/site_dir_'):]
            file_to_parse = path + '/' + files[0]

            logging.debug(f'Start scrapping site: {site_name}')

            with open(file_to_parse, 'rb') as file:
                html_content = str(file.read())

                # Get phones and emails
                try:
                    phone_email_data: ContactsData = get_phone_and_email(content=html_content)
                    logging.debug(f'Successfully get emails and phones for: {site_name}')
                except Exception as e:
                    logging.error(f'GETTING CONTACTS: {e}')

                # Get information about company
                try:
                    information_data: CompanyInfoData = get_company_info(content=html_content)
                    logging.debug(f'Successfully get information for: {site_name}')
                except Exception as e:
                    logging.error(f'GETTING INFORMATION: {e}')

                # pprint(information_data)

                file.close()
