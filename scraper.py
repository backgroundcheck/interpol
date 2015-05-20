import dataset
import requests
from urlparse import urljoin
from lxml import html
from normality import slugify
from itertools import count

engine = dataset.connect('sqlite:///data.sqlite')
notices = engine['data']


def scrape_case(url):
    res = requests.get(url)
    # empty = 'class="nom_fugitif_wanted">Identity unknown</div>' not in res.content
    #if empty:
    #     print "MISSING", url
    #    return
    doc = html.fromstring(res.content)
    data = {
        'url': url,
        'name': doc.find('.//div[@class="nom_fugitif_wanted"]').text_content(),
        'reason': doc.find('.//span[@class="nom_fugitif_wanted_small"]').text_content(),
        # 'html': res.content
    }
    for row in doc.findall('.//div[@class="bloc_detail"]//tr'):
        title, value = row.findall('./td')
        name = slugify(title.text_content(), sep='_')
        data[name] = value.text_content().strip()

    print [data['name']]
    notices.upsert(data, ['url'])


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
