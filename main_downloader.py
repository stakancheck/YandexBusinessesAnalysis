from bs4 import BeautifulSoup as bs4
from tqdm.asyncio import tqdm
import aiohttp
import asyncio
import aiofiles
import logging
import os
import pandas as pd

logging.basicConfig(level=logging.DEBUG, filename='logs.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
ONE_FILE = True
TIMEOUT = 10
PROGRESS_BAR_ASCII = False


class DownloadSite:
    def __init__(self, url: str, protocol: str = 'http://'):
        self.protocol = protocol
        self.site = url
        self.url = protocol + url
        self.links = {self.url}
        self.main_page = True

    async def get_page_content(self, sub_url: str):
        logging.debug(f'Start get site by url: {self.site} -> {sub_url}')

        async with aiohttp.ClientSession(trust_env=True) as session:
            try:
                async with session.get(sub_url, ssl=False, timeout=TIMEOUT) as resp:
                    logging.info(f'STATUS {resp.status}: {self.site} -> {sub_url}')
                    if resp.status == 200:
                        await self.write_to_file(content=await resp.read(), sub_url=sub_url)
                    elif resp.status == 403:
                        self.url = 'https://' + self.site
                        await self.get_page_content(sub_url=self.url)
                    else:
                        logging.error(f'While getting page {self.site} -> {sub_url}')

            # except aiohttp.TooManyRedirects as ex:
            #     logging.error(f'{ex}: {self.site} -> {sub_url}')
            #
            # except asyncio.exceptions.TimeoutError as ex:
            #     logging.error(f'{ex}: {self.site} -> {sub_url}')
            #
            # except aiohttp.ClientConnectorError as ex:
            #     logging.error(f'{ex}: {self.site} -> {sub_url}')

            except Exception as ex:
                logging.error(f'{ex}: {self.site} -> {sub_url}')

    async def write_to_file(self, content, sub_url: str):
        if ONE_FILE:
            logging.debug(f'Start write content to one file: {self.site}/save.html')
            async with aiofiles.open(f'downloader/site_dir_{self.site}/save.html', 'ab+') as file:
                await file.write(content)
                await file.flush()
        else:
            filename = sub_url[7:].replace('/', '_')
            logging.debug(f'Start write content to one file: {self.site}/{filename}.html')
            try:
                async with aiofiles.open(f'downloader/site_dir_{self.site}/{filename}_save.html', 'wb+') as file:
                    await file.write(content)
                    await file.flush()
            except Exception as ex:
                print(ex)
        logging.info(f'Content has successfully written: {sub_url}')

        if self.main_page:
            self.main_page = False
            internal_links = await self.find_links(content, sub_url)
            await self.start_downloading_list(links_list=internal_links)

    async def __call__(self, *args, **kwargs):
        os.makedirs(f'downloader/site_dir_{self.site}', exist_ok=True)
        await self.start_downloading_list(links_list={self.url})

    async def start_downloading_list(self, links_list: set):
        for site in links_list:
            await self.get_page_content(sub_url=site)

    async def find_links(self, content: bytes, sub_url: str):
        local_links = []
        logging.debug(f'Start catching up links for page: {self.site} -> {sub_url}')
        html = content.decode("utf-8")
        soup = bs4(html, 'html.parser')
        for link in soup.find_all("a", href=True):
            url: str = link['href']

            if url in local_links or url in self.links:
                continue

            if ('catalog' in url) or ('product' in url) or \
                    ('service' in url) or ('model' in url) or \
                    ('category' in url) or ('wp-content' in url) or not('/' in url):
                continue

            if url.startswith('http://' + self.site):
                if url[len('http://' + self.site):].startswith('/#'):
                    continue
            elif url.startswith('https://' + self.site):
                if url[len('https://' + self.site):].startswith('/#'):
                    continue

            if url.startswith('http'):
                if not(self.site in url):
                    continue  # Встретили ссылку на внешний ресурс
            elif url.startswith('/#'):
                continue
            elif url.startswith('/'):
                url = self.url + url
            else:
                url = self.url + '/' + url

            if url == f'http://{self.site}' or \
                    url == f'http://{self.site}/' or \
                    url == f'https://{self.site}' or \
                    url == f'https://{self.site}/':
                continue

            logging.debug(f'Found internal link for {self.site} -> {url}')
            local_links.append(url)
            self.links.add(url)

        return set(local_links)


async def main():
    def get_urls_from_database():
        all_urls = pd.read_csv('all_urls.csv', delimiter='\t')
        urls = all_urls.iloc[:, 0].tolist()
        urls.append(all_urls.keys()[0])
        return urls

    urls = get_urls_from_database()

    logging.info('START WORKING')

    for site_url in tqdm(urls[:4000], ascii=PROGRESS_BAR_ASCII, desc='Main progress'):
        await DownloadSite(url=site_url)()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
