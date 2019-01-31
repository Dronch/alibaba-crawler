from .SeleniumHelper import SeleniumHelper
from urllib.parse import urlsplit
from tqdm import tqdm
import requests
import os
import re
import xlsxwriter
import signal


class AlibabaSelenium(SeleniumHelper):

    def __init__(self, driver_path, request_delay, wait_time, timeout, proxy, headless, outfile):

        self.workbook = xlsxwriter.Workbook(outfile)

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
        self.workbook.close()

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
                    if self.getValue(a) == category:
                        href = self.getAttribute(a, 'href')
                        a.click()
                        if not href:
                            a = self.getElementFrom(a.find_element_by_xpath('..'), 'ul li:last-child a')
                            a.click()
                        no_err = True
                        break
                assert no_err
        except:
            print("Can't crawl {}".format(store_url))
            return

        worksheet = self.workbook.add_worksheet(
            name='{} - {}'.format(re.search(r'.*?\/\/(.*?)\.', store_url).group(1), category))
        worksheet.set_default_row(120)
        worksheet.set_column('A:B', 40)
        worksheet.set_column('C:Z', 20)

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
                price = self.getElementValue('.price-ladder')
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
                                worksheet.write('A{}'.format(current_row), item['url'])
                                worksheet.write('B{}'.format(current_row), item['description'])
                                worksheet.write('C{}'.format(current_row), item['price'])

                                char = 'D'
                                for img in item['images']:
                                    worksheet.insert_image('{}{}'.format(char, current_row),
                                                           os.path.join('images', img['filename']),
                                                           {
                                                               'url': item['url'],
                                                               'x_scale': 1 / 7,
                                                               'y_scale': 1 / 7,
                                                               'x_offset': 5,
                                                               'y_offset': 5
                                                           })
                                    char = chr(ord(char) + 1)

                                current_row += 1

                if next_page is not None:
                    self.loadPage(next_page)
                    get_items_urls(page_num + 1, current_row)
            except:
                pass

        get_items_urls()
