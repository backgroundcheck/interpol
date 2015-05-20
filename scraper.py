import dataset
import requests
from urlparse import urljoin
from lxml import html
from itertools import count

engine = dataset.connect('sqlite:///data.sqlite')
notices = engine['data']


def scrape_case(url):
    if notices.find_one(url=url):
        return
    res = requests.get(url)
    empty = 'class="nom_fugitif_wanted">Identity unknown</div>' not in res.content
    if not empty:
        print "FOUND", url
    notices.insert({
        'url': url,
        'empty': empty,
        'html': None if empty else res.content
    })


def scrape():
    url = 'http://www.interpol.int/notice/search/wanted/(offset)/%s'
    for i in count(0):
        p = i * 9
        res = requests.get(url % p)
        print 'RES', res.url
        doc = html.fromstring(res.content)
        links = doc.findall('.//div[@class="wanted"]//a')
        if not len(links):
            return
        for link in links:
            case_url = urljoin(url, link.get('href'))
            scrape_case(case_url)


if __name__ == '__main__':
    scrape()
