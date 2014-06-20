import sys
import os
import lxml.html
import lxml
import re
import requests 
import subprocess

firefox = {'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
class WebCrawler:

    def __init__(self, user_input):
        self.url = user_input

    #Method for init lxml object of page content
    def get_page(self, url):
        raw_content = requests.get(url, headers=firefox).text.encode('utf8')
        return lxml.html.fromstring(raw_content)

    #Download products image to specified folder
    def download_image(slef, url, product_name):
        folder = 'cover/' + product_name.replace(' ', '_') + '/' + re.sub(r'^http\:\/\/(.*)\/(.*)\/(.*)\/', '', url)
        print folder
        subprocess.call(['curl', '--create-dirs', '-o', folder, url]) 
        print "Download Success"
        return

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

        #function for prompt selection for user, and getting selection from user
        def get_selection(user_input):
            num = 0
            for el_section in user_input:
                print str(num) + ':' + el_section
                num += 1
            print "Please choose a section number:"
            selection = raw_input()
            return user_input[int(selection)]

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
        if department:
            front_page = self.get_page(url)
            sections = [ cat_section.text for cat_section in front_page.xpath("//div[@id='refinements']//h2") ]
            selection = get_selection(sections)
            s = front_page.xpath("//h2[text()=$name]", name = selection )[0].getnext()
            option = {}
            for el_link in s.xpath(".//a[@href][re:match(@href, '\/s\/(.*)')]", namespaces={'re': 'http://exslt.org/regular-expressions'}):
                try:
                    option[el_link.xpath('./span/text()')[0]] = el_link.attrib['href']
                except:
                    pass
            get_products_image(domain_name, option[get_selection(option.keys())])
        else:
            print 'not match'
try:
    user_input = sys.argv[1]
except IndexError:
    user_input = False

crawler = WebCrawler(user_input)
crawler.get_amazon_image('http://www.amazon.co.uk/DVDs-Blu-ray-box-sets/b/ref=sa_menu_dvd_blu?ie=UTF8&node=283926', 'www.amazon.co.uk')
