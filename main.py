import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch(url):
    return requests.get(url).content

def get_links(url, links):
    html = fetch(url)
    document = BeautifulSoup(html, 'html.parser')
    a_tags = document.select('.rtbf-lis-only article header a')
    collected_links = links + list(map( (lambda a:a['href']), a_tags))
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

url = 'https://www.rtbf.be/auvio/archives?pid=9258&contentType=complete'

links = catalog_links(url)

print(links)



