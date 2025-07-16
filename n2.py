import re
import urllib.parse
from html.parser import HTMLParser
from helpers import retrieve_url
from novaprinter import prettyPrinter

class nyaasi_parser(HTMLParser):
    def __init__(self, engine_url):
        super().__init__()
        self.engine_url = engine_url
        self.inside_result = False
        self.results = []
        self.curr = {}
        self.td_index = 0
        self.capture_data = False
        self.magnet = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'tr' and 'class' in attrs:
            self.inside_result = True
            self.curr = {}
            self.td_index = 0
        elif self.inside_result and tag == 'a' and 'href' in attrs:
            href = attrs['href']
            if href.startswith('magnet:'):
                self.curr['link'] = href
                self.curr['engine_url'] = self.engine_url
            elif re.match(r'/view/\d+', href):
                self.capture_data = True
        elif self.inside_result and tag == 'td':
            self.td_index += 1
            self.capture_data = True

    def handle_endtag(self, tag):
        if tag == 'tr' and self.inside_result:
            self.inside_result = False
            if all(k in self.curr for k in ('name', 'size', 'seeds', 'leech', 'link')):
                self.results.append(self.curr)
            self.curr = {}
            self.capture_data = False

    def handle_data(self, data):
        if self.capture_data:
            text = data.strip()
            if text:
                if 'name' not in self.curr:
                    self.curr['name'] = text
                elif self.td_index == 2 and 'size' not in self.curr:
                    self.curr['size'] = text
                elif self.td_index == 5 and 'seeds' not in self.curr:
                    self.curr['seeds'] = text
                elif self.td_index == 6 and 'leech' not in self.curr:
                    self.curr['leech'] = text
            self.capture_data = False

class nyaasi:
    url = 'https://nyaa.si'
    name = 'NyaaSi2'
    supported_categories = {'all': ''}

    def search(self, what, cat='all'):
        query = urllib.parse.quote_plus(what)
        search_url = f'{self.url}/?f=0&c=0_0&q={query}&s=seeders&o=desc'
        html = retrieve_url(search_url)
        parser = nyaasi_parser(self.url)
        parser.feed(html)
        for result in parser.results:
            prettyPrinter(result)
