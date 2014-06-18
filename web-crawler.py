import sys
import os
import lxml.html
import lxml
import re
import requests

class WebCrawler:
    def __init__(self, user_input):
        self.url = user_input

    def validate_url(self):
        if self.url:
            try:
                requests.get(self.url, timeout=30)
            except requests.exceptions.RequestException, e:
                print('Reason:\n %s' % str(e))
                print('Please input a valid URL')
                self.url = raw_input(':')
                self.validate_url()
            return self.url
        else:
            print('Please input URL')
            self.url = raw_input(':')
            self.validate_url()

    def fetch_content(self):
        url = self.validate_url()
        html = requests.get(url)
        content = lxml.html.fromstring(html.text)
        links_dict = {}
        for element in content.xpath('//a[@href]'):
            try:
                links_dict[element.text.strip()] = element.attrib['href']
            except:
                pass
        return links_dict

    def get_amazon_image(self, url, domain_name):
        department_url_pattern = '^http\:\/\/' + domain_name + '\/[a-zA-z]{2,}(.*)$'
        department = re.match(department_url_pattern, url)
        if department:
            firefox = {'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
            content = requests.get(url, headers=firefox).text.encode('utf8')
            html = lxml.html.fromstring(content)
            for i in html.xpath("//a[@href][re:match(@href, '\/s\/(.*)')]", namespaces={'re':'http://exslt.org/regular-expressions'}):
                try:
                    text = i.xpath('./span/text()')[0]
                    if text == 'DVD':
                        print i.attrib['href']
                except:
                    pass
        else:
            print 'not match'

try:
    user_input = sys.argv[1]
except IndexError:
    user_input = False

crawler = WebCrawler(user_input)
crawler.get_amazon_image('http://www.amazon.co.uk/DVDs-Blu-ray-box-sets/b/ref=sa_menu_dvd_blu?ie=UTF8&node=283926', 'www.amazon.co.uk')
