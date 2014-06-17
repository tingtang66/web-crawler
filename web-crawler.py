import sys
import os
import lxml.html
import lxml
import re
import requests

class WebCrawler:
    def __init__(self, user_input):
        self.url = user_input

    def __validate_url(self):
        if self.url: 
            try:
                requests.get(self.url, timeout=30)
            except requests.exceptions.RequestException, e:
                print('Reason:\n %s' % str(e))
                print('Please input a valid URL')
                self.url = raw_input(':')
                self.__validate_url()
            return self.url
        else:
            print('Please input URL')
            self.url = raw_input(':')
            self.__validate_url()

    def fetch_content(self):
        self.__validate_url() 
        print self.url
        
try:
    user_input = sys.argv[1]
except IndexError:
    user_input = False

crawler = WebCrawler(user_input)
crawler.fetch_content()
#html = lxml.html.fromstring(requests.get(crawler.validate_url()).text)
#for item in html.xpath('//a/@href'):
#    print item
