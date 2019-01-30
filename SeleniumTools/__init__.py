from .SeleniumHelper import SeleniumHelper
from urllib.parse import urlsplit
from tqdm import tqdm
import requests
import os
import re


class AlibabaSelenium(SeleniumHelper):

    def __init__(self, driver_path, request_delay, wait_time, timeout, proxy, headless):
        SeleniumHelper.WAIT = wait_time
        SeleniumHelper.TIMEOUT = timeout
        SeleniumHelper.DELAY = request_delay
        SeleniumHelper.__init__(self,
                                driver_path=driver_path,
                                proxy=proxy,
                                headless=headless)

    def crawl(self, store_url, outfile, min_price, max_price):
        try:
            print('Starting with {}'.format(store_url))
            mobile_url = "{0.scheme}://m.{0.netloc}/".format(urlsplit(store_url))
            self.loadPage(mobile_url)
            product_list_btn = self.waitShowElement(r'li[data-page-name="products"]')
            product_list_btn.click()
        except:
            print("Can't crawl {}".format(store_url))
            return

        def get_item(url):
            try:
                self.loadPage(url)
                #self.waitShowElement('ul.inav.util-clearfix li:last-child a')
                images = []
                for img in self.getElements('.slide img'):
                    try:
                        img_url = self.getAttribute(img, 'src').replace('_640x640xz.jpg', '')
                        img_data = requests.get(img_url).content
                        filename = img_url.split('/')[-1]
                        with open(os.path.join('images', filename), 'wb') as handler:
                            handler.write(img_data)
                        images.append(dict(url=img_url, filename=filename))
                    except:
                        pass
                description = self.getElementValue('.product-title h1')
                price = self.getElementValue('.price')
            except:
                return None
            return dict(images=images, description=description, price=price, url=url)

        def get_items_urls(page_num=1):
            try:
                print('Crawl to product list page number {}'.format(page_num))
                self.waitShowElement('.item.clearfix:last-child ul.params li.param:last-child span')
                items = self.getElements('.item.clearfix')

                urls = [{
                    'href': self.getAttribute(self.getElementFrom(item, 'a'), 'href'),
                    'price': self.getElementFromValue(item, 'ul.params li.param:last-child span')
                } for item in items]

                next_page = self.getElementAttribute('a.ui-pager-next:not([rel=nofollow])', 'href')

                for url in tqdm(urls):
                    try:
                        price = float(re.search(r'\$(([0-9]*[.])?[0-9]+)', url['price']).group(1))
                    except:
                        price = None

                    if price:
                        if price >= min_price and price <= max_price:
                            item = get_item(url['href'])
                            if item:
                                img_data = ';'.join(
                                    ['{};{}'.format(img['url'], img['filename']) for img in item['images']])
                                row = '{};{};{};{};{}\n'.format(store_url, item['url'], item['description'],
                                                                item['price'], img_data)
                                open(outfile, 'a').write(row)

                if next_page is not None:
                    self.loadPage(next_page)
                    get_items_urls(page_num + 1)
            except:
                pass

        get_items_urls()
