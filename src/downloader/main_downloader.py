import os
import logging
import requests
import pandas as pd
import concurrent.futures

from pathlib import Path
from urllib3 import Retry
from datetime import datetime
from bs4 import BeautifulSoup as bs4
from requests.adapters import HTTPAdapter


PROJECT_DIR = str(Path(__file__).parent.parent.parent)
logging.basicConfig(level=logging.DEBUG,
                    filename='../../logs.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class MainDownloader:
    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }

    TIMEOUT = 5
    IGNORE_LIST = ['drom.com', 'catalog', 'product', 'model',
                   'wp-content', 'category', 'categories',
                   'product', 'marki', 'news', 'novosti', 'assets', 'upload', 'cache']

    @staticmethod
    def download_site(domain: str):
        logging.debug(f'Start downloading site: {domain}')

        # Костыль
        if 'drom.com' in domain:
            return None

        session = requests.Session()
        retry = Retry(total=3, connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        try:
            master_url = f'https://{domain}'

            response = session.get(url=master_url,
                                   headers=MainDownloader.HEADERS,
                                   timeout=MainDownloader.TIMEOUT)

            if response.status_code == 200:
                links = MainDownloader.get_links(html_content=response.content,
                                                 master_link=master_url,
                                                 domain=domain,
                                                 encoding=response.encoding)
                MainDownloader.download_sub_pages(links_subpages=links, domain=domain)
            else:
                logging.error(f'Response {response.status_code} of main page: {domain}')

        except Exception as e:
            logging.error(f'While getting main page: {domain}: Error: {e}')

    @staticmethod
    def check_url(url: str, domain: str, master_link: str) -> bool:
        for ignore in MainDownloader.IGNORE_LIST:
            if ignore in url:
                return False

        if url.startswith('/#') or url.startswith(master_link + '/#') \
                or not ('/' in url) or url.count('/') > 5:
            return False

        if '.com' in url or '.ru' in url or '.site' in url:
            if not (domain in url):
                return False

        return url.startswith('http') and not(domain in url)

    @staticmethod
    def get_links(html_content: bytes, master_link: str, domain: str, encoding: str = 'utf-8') -> list[str]:
        logging.debug(f'Start get links for: {domain}')
        local_links = [master_link]
        html = html_content.decode(encoding=encoding)
        soup = bs4(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            url: str = link['href']

            if MainDownloader.check_url(url=url, domain=domain, master_link=master_link):
                if url.startswith('/'):
                    url = master_link + url
                elif not url.startswith('http'):
                    url = master_link + '/' + url
                if not (url in local_links):
                    local_links.append(url)

        logging.info(f'Successfully found {len(local_links)} subpages for {domain}')

        return local_links

    @staticmethod
    def download_sub_pages(links_subpages: list[str], domain: str):
        session = requests.Session()
        retry = Retry(total=3, connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        for link in links_subpages:
            try:
                response = session.get(url=link,
                                       headers=MainDownloader.HEADERS,
                                       timeout=MainDownloader.TIMEOUT)

                if response.status_code == 200:
                    try:
                        MainDownloader.write_to_file(content=response.content,
                                                     domain=domain)
                        logging.info(f'Successfully save subpage: {link}')
                    except Exception as e:
                        logging.error(f'While save subpage: {link}: Error: {e}')

                else:
                    logging.error(f'Response {response.status_code} of subpage: {link}')

            except Exception as e:
                logging.error(f'While getting subpage: {link}: Error: {e}')

    @staticmethod
    def write_to_file(content: bytes, domain: str):
        os.makedirs(f'{PROJECT_DIR}/downloader2/site_dir_{domain}', exist_ok=True)
        with open(f'{PROJECT_DIR}/downloader2/site_dir_{domain}/save.html', 'ab+') as file:
            file.write(content)
            file.close()


def main():
    def get_urls_from_database():
        all_urls = pd.read_csv(PROJECT_DIR + '/all_urls.csv', delimiter='\t')
        res = all_urls.iloc[:, 0].tolist()
        res.append(all_urls.keys()[0])
        return res

    domains = get_urls_from_database()[:100]

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        executor.map(MainDownloader.download_site, domains)


if __name__ == '__main__':
    start_time = datetime.now()
    logging.info(f'START WORKING AT {start_time}')
    main()
    finish_time = datetime.now()
    logging.info(f'FINISHED! TIME TO EXECUTE: {finish_time - start_time}')
