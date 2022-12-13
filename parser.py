import os
import pandas as pd
from tqdm.asyncio import tqdm
from bs4 import BeautifulSoup as bs4


with open('downloader/site_dir_avtotsentr-kgs-ulitsa-60-let-oktjabrja.clients.site/save.html', 'r') as file:
    content = file.read()
    soup = bs4(content, 'html.parser')