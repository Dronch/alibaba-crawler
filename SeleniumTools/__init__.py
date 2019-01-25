from .SeleniumHelper import SeleniumHelper
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
        print('Starting with {}'.format(store_url))
        self.loadPage(store_url)
        product_list_btn = self.waitShowElement(r'.navigation.fix a.nav-link[href^="/productlist.html"]')
        product_list_btn.click()

        def get_items_urls(page_num=1):
            try:
                print('Product list page number {}'.format(page_num))
                self.waitShowElement('.icbu-product-list.gallery-view .next-row:last-child .fav-container:last-child')
                items = self.getElements('.icbu-product-list.gallery-view .product-item')

                result = [{
                    'href': self.getAttribute(self.getElementFrom(item, 'a.product-image'), 'href'),
                    'price': self.getElementFromValue(item, 'span.num')
                } for item in items]

                next_page = self.getElement('i.next-icon.next-icon-arrow-right.next-icon-medium.next-icon-last')
                print(self.getAttribute(next_page, 'data-spm-anchor-id'))
                if self.getAttribute(next_page, 'data-spm-anchor-id'):
                    next_page.click()
                    result = result + get_items_urls(page_num + 1)
            except:
                return []
            return result

        def get_item(url):
            try:
                self.loadPage(url)
                #self.waitShowElement('ul.inav.util-clearfix li:last-child a')
                images = []
                for img in self.getElements('ul.inav.util-clearfix li img'):
                    try:
                        img_url = self.getAttribute(img, 'src').replace('_50x50.jpg', '')
                        img_data = requests.get(img_url).content
                        filename = img_url.replace('/', '_')
                        with open(os.path.join('images', filename), 'wb') as handler:
                            handler.write(img_data)
                        images.append(dict(url=img_url, filename=filename))
                    except:
                        pass
                description = self.getElementValue('h1.ma-title')
                price = self.getElementValue('span.pre-inquiry-price')
            except:
                return None
            return dict(images=images, description=description, price=price, url=url)

        print('Collecting product hrefs...')
        urls = get_items_urls()
        print('Total {} products will crawled'.format(len(urls)))
        for url in tqdm(urls):
            try:
                price = float(re.search(r'\$(([0-9]*[.])?[0-9]+)', url['price']).group(1))
            except:
                price = None
            if price:
                if price >= min_price and price <= max_price:
                    item = get_item(url['href'])
                    if item:
                        img_data = ';'.join(['{};{}'.format(img['url'], img['filename']) for img in item['images']])
                        row = '{};{};{};{};{}\n'.format(store_url, item['url'], item['description'],
                                                        item['price'], img_data)
                        open(outfile, 'a').write(row)
