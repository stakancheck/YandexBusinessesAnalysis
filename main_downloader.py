import os
import sys
import logging
import requests
import pandas as pd
import concurrent.futures
from datetime import datetime

from bs4 import BeautifulSoup as bs4

logging.basicConfig(level=logging.DEBUG,
                    filename='logs.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class MainDownloader:
    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }

    TIMEOUT = 10

    @staticmethod
    def download_site(domain: str):
        logging.debug(f'Start downloading site: {domain}')

        try:
            master_url = f'https://{domain}'
            response = requests.get(url=master_url,
                                    headers=MainDownloader.HEADERS,
                                    timeout=MainDownloader.TIMEOUT)

            if response.status_code == 403:
                master_url = f'http://{domain}'
                response = requests.get(url=master_url,
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
    def get_links(html_content: bytes, master_link: str, domain: str, encoding: str = 'utf-8') -> list[str]:
        logging.debug(f'Start get links for: {domain}')
        local_links = [master_link]
        html = html_content.decode(encoding=encoding)
        soup = bs4(html, 'html.parser')
        for link in soup.find_all("a", href=True):
            url: str = link['href']

            if ('catalog' in url) or ('product' in url) or \
                    ('service' in url) or ('model' in url) or \
                    ('category' in url) or ('wp-content' in url) or not ('/' in url):
                continue

            if url.startswith('/#') or url.startswith(master_link + '/#'):
                continue

            if url.startswith('http'):
                if domain in url:
                    continue
            elif url.startswith('/'):
                url = master_link + url
            else:
                url = master_link + '/' + url

            if url in local_links:
                continue

            local_links.append(url)

        logging.info(f'Successfully found {len(local_links)} subpages for {domain}')

        return local_links

    @staticmethod
    def download_sub_pages(links_subpages: list[str], domain: str):
        for link in links_subpages:
            try:
                response = requests.get(url=link,
                                        headers=MainDownloader.HEADERS,
                                        timeout=MainDownloader.TIMEOUT)

                if response.status_code == 403:
                    if link.startswith('http://'):
                        link = 'https://' + link[7:]
                    else:
                        link = 'http://' + link[8:]
                    response = requests.get(url=link,
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
        os.makedirs(f'downloader2/site_dir_{domain}', exist_ok=True)
        with open(f'downloader2/site_dir_{domain}/save.html', 'ab+') as file:
            file.write(content)
            file.close()


def main():
    def get_urls_from_database():
        all_urls = pd.read_csv('all_urls.csv', delimiter='\t')
        res = all_urls.iloc[:, 0].tolist()
        res.append(all_urls.keys()[0])
        return res

    domains = get_urls_from_database()[50:150]

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        executor.map(MainDownloader.download_site, domains)


if __name__ == '__main__':
    start_time = datetime.now()
    logging.info(f'START WORKING AT {start_time}')
    main()
    finish_time = datetime.now()
    logging.info(f'FINISHED! TIME TO EXECUTE: {finish_time - start_time}')
