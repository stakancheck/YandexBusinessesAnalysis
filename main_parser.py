import os
import csv
import logging

from pprint import pprint
from itertools import islice
from tqdm.asyncio import tqdm
from dataclasses import asdict
from contacts_parser import ContactsParser, ContactsData
from company_info_parser import CompanyInfoParser, CompanyInfoData


WRITE_HEADER = True
DOWNLOAD_DIR = 'downloader'
FILE_NAME = 'save.html'
PROGRESS_BAR_ASCII = False
HEADERS = ('url', 'name', 'phones', 'emails', 'general_director', 'type_of_company', 'registration_date',
           'founders', 'inn', 'ogrn', 'kpp', 'okpo', 'okato', 'oktmo', 'okogu', 'postal_code', 'address')

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


def iter_to_str(data: list) -> str:
    return '&'.join(data)


def transform_data_to_write(site_url: str, contacts: ContactsData, info: CompanyInfoData) -> list:
    logging.debug(f'Start write data to csv for: {site_url}')

    phones, emails = asdict(contacts).values()
    org_name, *over_info = asdict(info).values()

    data_to_write = [
        site_url,
        org_name,
        iter_to_str(phones),
        iter_to_str(emails),
        *list(map(iter_to_str, over_info))
    ]

    return data_to_write


if __name__ == '__main__':
    with open('database.csv', 'a+', encoding='UTF8') as file_db:

        db_writer = csv.writer(file_db)

        if WRITE_HEADER:
            db_writer.writerow(HEADERS)

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

                    # Start write data
                    data = transform_data_to_write(
                        site_url=site_name,
                        contacts=phone_email_data,
                        info=information_data
                    )

                    try:
                        db_writer.writerow(data)
                        file_db.flush()
                    except Exception as e:
                        logging.error(f'WRITING DATA: {e}')

                    file.close()

        file_db.close()