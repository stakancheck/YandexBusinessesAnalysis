from bs4 import BeautifulSoup as bs4
from tqdm.asyncio import tqdm
import aiohttp
import aioreq
import asyncio
import aiofiles
import logging
import os

cl = aioreq.Client()
logging.basicConfig(level=logging.DEBUG, filename='logs.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


class DownloadSite:
    def __init__(self, url: str, protocol: str = 'http://'):
        self.protocol = protocol
        self.site = url
        self.url = protocol + url
        self.links = {self.url: 'No'}

    async def get_page_content(self, sub_url: str):
        logging.debug(f'Start get site by url: {self.site} -> {sub_url}')
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sub_url, ssl=False, timeout=30) as resp:
                    logging.info(f'STATUS {resp.status}: {self.site} -> {sub_url}')
                    if resp.status == 200:
                        await self.write_to_file(content=await resp.read(), sub_url=sub_url)
                    else:
                        logging.error(f'While getting page {self.site} -> {sub_url}')
            except asyncio.exceptions.TimeoutError as ex:
                logging.error(f'TimeOutError while get page: {self.site} -> {sub_url}')

    async def write_to_file(self, content: bytes, sub_url: str):
        logging.debug(f'Start write content to file: {self.site}_{sub_url}')
        async with aiofiles.open(f'site_dir_{self.site}/{self.site}_save.html', 'ab+') as file:
            await file.write(content)
            await file.flush()
        logging.info(f'Content has successfully written: {self.site} -> {sub_url}')

    async def __call__(self, *args, **kwargs):
        os.makedirs(f'site_dir_{self.site}', exist_ok=True)
        for site in self.links:
            await self.get_page_content(sub_url=site)

    async def find_links(self, content: bytes, sub_url: str):
        logging.debug(f'Start catching up links for page: {self.site} -> {sub_url}')
        html = content.decode("utf-8")
        soup = bs4(html, 'html.parser')
        for link in soup.find_all("a", href=True):
            if str(link["href"]).startswith((str(website_link))):
                list_links.append(link["href"])


async def main():
    urls = ['avto-trakt.ru', 'special.mb-i.ru', 'выкупавто.su', '12322']

    # TODO: write script to get links from exel file

    logging.info('START WORKING')

    for site_url in tqdm(urls):
        await DownloadSite(url=site_url)()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
