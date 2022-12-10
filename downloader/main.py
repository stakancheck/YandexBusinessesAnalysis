from bs4 import BeautifulSoup as bs4
from tqdm.asyncio import tqdm
import aiohttp
import asyncio
import aiofiles
import logging
import os

logging.basicConfig(level=logging.DEBUG, filename='logs.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
ONE_FILE = False
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

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sub_url, ssl=False, timeout=TIMEOUT) as resp:
                    logging.info(f'STATUS {resp.status}: {self.site} -> {sub_url}')
                    if resp.status == 200:
                        await self.write_to_file(content=await resp.read(), sub_url=sub_url)
                    else:
                        logging.error(f'While getting page {self.site} -> {sub_url}')

            except asyncio.exceptions.TimeoutError as ex:
                logging.error(f'{ex}: {self.site} -> {sub_url}')

            except aiohttp.client_exceptions.ClientConnectorError as ex:
                logging.error(f'{ex}: {self.site} -> {sub_url}')

    async def write_to_file(self, content: bytes, sub_url: str):
        logging.debug(f'Start write content to file: {self.site}_{sub_url}')
        if ONE_FILE:
            async with aiofiles.open(f'site_dir_{self.site}/save.html', 'ab+') as file:
                await file.write(content)
                await file.flush()
        else:
            filename = sub_url[7:].replace('/', '_')
            async with aiofiles.open(f'site_dir_{self.site}/{filename}_save.html', 'wb+') as file:
                await file.write(content)
                await file.flush()
        logging.info(f'Content has successfully written: {self.site} -> {sub_url}')

        if self.main_page:
            self.main_page = False
            internal_links = await self.find_links(content, sub_url)
            await self.start_downloading_list(links_list=internal_links)

    async def __call__(self, *args, **kwargs):
        os.makedirs(f'site_dir_{self.site}', exist_ok=True)
        await self.start_downloading_list(links_list={self.url})

    async def start_downloading_list(self, links_list: set):
        for site in links_list:
            await self.get_page_content(sub_url=site)

    async def find_links(self, content: bytes, sub_url: str):
        local_links = []
        logging.debug(f'Start catching up links for page: {self.site} -> {sub_url}')
        html = content.decode("utf-8")
        soup = bs4(html, 'html.parser')
        for link in tqdm(soup.find_all("a", href=True), ascii=PROGRESS_BAR_ASCII, desc=f'Subpages for {self.site}'):
            url: str = link['href']

            # crutch with same link in html and main link: length diff > 2
            if self.site[7:] != url[7:] and \
                    self.site[7:] != url[8:] and \
                    '/' in url and \
                    (not 'catalog' in url) and \
                    (not url in local_links) and \
                    (not url in self.links):

                if not url.startswith('http'):
                    url = self.url + url

                logging.debug(f'Found internal link for {self.site} -> {url}')
                local_links.append(url)
                self.links.add(url)

        return set(local_links)


async def main():
    urls = ['avto-trakt.ru', 'special.mb-i.ru', 'выкупавто.su']

    # TODO: write script to get links from exel file

    logging.info('START WORKING')

    for site_url in tqdm(urls, ascii=PROGRESS_BAR_ASCII, desc='Main progress'):
        await DownloadSite(url=site_url)()


if __name__ == '__main__':
    asyncio.run(main())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
