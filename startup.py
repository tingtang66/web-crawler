from webcrawler import WebCrawler
import sys

firefox = {'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'}

try:
    user_input = sys.argv[1]
except IndexError:
    user_input = False

crawler = WebCrawler(user_input, firefox)
crawler.get_amazon_image(crawler.validate_url(), 'www.amazon.co.uk')
