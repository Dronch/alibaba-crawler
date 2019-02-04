from .SeleniumHelper import SeleniumHelper
from urllib.parse import urlsplit
from tqdm import tqdm
import requests
import os
import re
import signal


class AlibabaSelenium(SeleniumHelper):

    def __init__(self, driver_path, request_delay, wait_time, timeout, proxy, headless, outfile):

        self.outfile = outfile
        self.proxy = '' if proxy['proxy'] is None else proxy['proxy']

        self.proxies = {
            "http": self.proxy,
            "https": self.proxy,
        }

        SeleniumHelper.WAIT = wait_time
        SeleniumHelper.TIMEOUT = timeout
        SeleniumHelper.DELAY = request_delay
        SeleniumHelper.__init__(self,
                                driver_path=driver_path,
                                proxy=proxy,
                                headless=headless)

        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self):
        self.driver.close()

    def __del__(self):
        self.exit()

    def crawl(self, store_url, min_price, max_price, category=None):
        try:
            print('Starting with {}'.format(store_url))
            mobile_url = "{0.scheme}://m.{0.netloc}/".format(urlsplit(store_url))
            self.loadPage(mobile_url)
            product_list_btn = self.waitShowElement(r'li[data-page-name="products"]')
            product_list_btn.click()
            if category:
                self.getElement('#refine-btn').click()

                no_err = False
                for a in self.getElements('#categories-sidebar a'):
                    if self.getValue(a).lower() == category.lower():
                        href = self.getAttribute(a, 'href')
                        a.click()
                        if not href:
                            a = self.getElementFrom(a.find_element_by_xpath('..'), 'ul li:last-child a')
                            a.click()
                        no_err = True
                        break
                if not no_err:
                    print("Can't crawl {}: can't find '{}' category".format(store_url, category))
                    return
        except:
            print("Can't crawl {}".format(store_url))
            return

        def get_item(url):
            try:
                self.loadPage(url)
                images = []
                for img in self.getElements('.slide img'):
                    try:
                        img_url = self.getAttribute(img, 'data-src')\
                            .replace('_640x640xz.jpg', '').replace('_640x640xz.png', '')
                        response = requests.get(img_url, proxies=self.proxies) if self.proxy else requests.get(img_url)
                        img_data = response.content
                        filename = img_url.split('/')[-1]
                        with open(os.path.join('images', filename), 'wb') as handler:
                            handler.write(img_data)
                        images.append(dict(url=img_url, filename=filename))
                    except Exception as e:
                        print(e)
                        pass
                description = self.getElementValue('.product-title h1')
                price = self.getElementValue('.price')
                price = self.getElementValue('.price-ladder') if price is None else price
            except:
                return None
            return dict(images=images, description=description, price=price, url=url)

        def get_items_urls(page_num=1, current_row=1):

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
                                url = "{0.scheme}://{0.netloc}{1.path}".format(urlsplit(store_url),
                                                                               urlsplit(item['url']))
                                row = '{};{};{};{};{};{}\n'.format(store_url,
                                                                   url,
                                                                   category if category else '',
                                                                   item['description'],
                                                                   item['price'], img_data)
                                open(self.outfile, 'a').write(row)

                if next_page is not None:
                    self.loadPage(next_page)
                    get_items_urls(page_num + 1, current_row)
            except:
                pass

        get_items_urls()
