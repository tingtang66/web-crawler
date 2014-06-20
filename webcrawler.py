import sys
import os
import lxml.html
import lxml
import re
import requests 
import subprocess

class WebCrawler:

    def __init__(self, user_input, user_agent):
        self.domain_name = user_input
        self.agent = user_agent
        self.cookies = requests.get(self.validate_url()[1], headers = self.agent).cookies

    #Method for init lxml object of page content
    def get_page(self, url):
        raw_content = requests.get(url, headers = self.agent).text.encode('utf8')
        return lxml.html.fromstring(raw_content)

    #Download products image to specified folder
    def download_image(slef, url, product_name):
        folder = 'cover/' + product_name.replace(' ', '_') + '/' + re.sub(r'^http\:\/\/(.*)\/(.*)\/(.*)\/', '', url)
        print folder
        subprocess.call(['curl', '--create-dirs', '-o', folder, url]) 
        print "Download Success"
        return

    #Make sure the url or domain is working
    #Return domain name and full URL with http://
    def validate_url(self):
        if self.domain_name:
            try:
                requests.get('http://' + self.domain_name, timeout=30)
            except requests.exceptions.RequestException, e:
                print('Reason:\n %s' % str(e))
                print('Please input a valid URL')
                self.domain_name = raw_input(':')
                self.validate_url()
        else:
            print('Please input URL')
            self.domain_name = raw_input(':')
            self.validate_url()
        domain_name = self.domain_name
        url = 'http://' + domain_name
        return domain_name, url

    #function for prompt selection for user, and getting selection from user
    #'sections' must be a list!
    def get_selection(self, sections):
        num = 0
        for el_section in sections:
            print str(num) + ':' + el_section
            num += 1
        print "Please choose a section number:"
        selection = raw_input()
        return selection, sections[int(selection)]

    def pick_department(self):
        cats = []
        subcats_url = {}
        domain_name, url = self.validate_url()
        front_page = self.get_page(url)
        for li in front_page.xpath("//ul[@id='nav_cats']//li"):
            if li.text:
                cats.append(li.text)
        cats_num = self.get_selection(cats)[0]
        subcats_id = 'nav_subcats_' + str(cats_num)
        for subcats in front_page.xpath("//div[@id='nav_subcats']//div[@id=$id]//a", id = subcats_id):
            if subcats.text:
                subcats_url[subcats.text] = subcats.attrib['href']
        return domain_name, subcats_url[self.get_selection(subcats_url.keys())[1]]

    def get_amazon_image(self):
        domain_name, absolute_path = self.pick_department()
        url = 'http://' + domain_name + absolute_path

        #Get products
        def get_products_image(domain_name, absolute_path):
            internal_page_url = 'http://' + domain_name + absolute_path
            internal_page = self.get_page(internal_page_url)
            el_num = 0
            while el_num <24:
                el = 'result_' + str(el_num)
                products_page = self.get_page(internal_page.xpath("//div[@id='resultsCol']//div[@id=$result]//a", result=el)[0].attrib['href'])
                tag_attrib = products_page.xpath("//img[@id='main-image']")[0].attrib
                product_name = internal_page.xpath("//div[@id='resultsCol']//div[@id=$result]//h3//span/text()", result=el)[0]
                print product_name
                self.download_image(tag_attrib['src'], product_name)
                self.download_image(tag_attrib['rel'], product_name)
                el_num += 1
            if internal_page.xpath("//a[@title='Next Page']")[0].attrib['href']: 
                get_products_image(domain_name, internal_page.xpath("//a[@title='Next Page']")[0].attrib['href'])
            else:
                print "You have got all the image you would download"
                return

        #initial page and breakdown page to find the usable hrefs
        front_page = self.get_page(url)
        sections = [ cat_section.text for cat_section in front_page.xpath("//div[@id='refinements']//h2") ]
        selection = self.get_selection(sections)[1]
        s = front_page.xpath("//h2[text()=$name]", name = selection )[0].getnext()
        option = {}
        for el_link in s.xpath(".//a[@href][re:match(@href, '\/s\/(.*)')]", namespaces={'re': 'http://exslt.org/regular-expressions'}):
            try:
                option[el_link.xpath('./span/text()')[0]] = el_link.attrib['href']
            except:
                pass
        get_products_image(domain_name, option[self.get_selection(option.keys())[1]])
