import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import youtube_dl
import re

def fetch(url):
    return requests.get(url).content

def get_title(header):
    title = header.find('h5')
    if title is None:
        title = header.find('h4')
    pattern = re.compile(re.escape('HISTOIRE -'), re.IGNORECASE)
    txt = pattern.sub('', title.text)
    return txt.strip()

def get_url(header):
    return header.find('a')['href']

def get_links(url, links):
    html = fetch(url)
    document = BeautifulSoup(html, 'html.parser')
    headers = document.select('article.rtbf-media-li header')
    collected_links = links + list(map( (lambda h:{'title': get_title(h), 'url': get_url(h)}), headers))
    follow_up = next_page(url, document)
    if follow_up is None:
        return collected_links
    return get_links(follow_up, collected_links)

def next_page(base_url, document):
    pagination = document.select('.rtbf-pagination [aria-label="Next"]')
    if not pagination:
        return None
    page = pagination[0]
    if page.find_parents('li', class_='disabled'):
        return None
    return urljoin(base_url, page['href'])

def catalog_links(url):
    return get_links(url, [])

class ErrorLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def ydl_hooks(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
        'preferredquality': '256',
    }],
    'logger': ErrorLogger(),
    'progress_hooks': [ydl_hooks],
    'download_archive': '.auviocache',
}

initial_url = 'https://www.rtbf.be/auvio/archives?pid=9258&contentType=complete'

links = catalog_links(initial_url)

for link in links:
    opts = dict(ydl_opts, **{ 
        'outtmpl': 'downloads/{title}.%(ext)s'.format(**link)
    })
    print('Downloading "{title}" [{url}]...'.format(**link))
    with youtube_dl.YoutubeDL(opts) as ydl:
        url = link['url']
        ydl.download([link['url']])

